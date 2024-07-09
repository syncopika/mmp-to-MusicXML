import logging
import sys
import xml.etree.ElementTree as ET

from collections import OrderedDict
from typing import List
from xml.dom import minidom

from mmp_to_musicxml.utils.note_checker import NoteChecker
from mmp_to_musicxml.utils.key_sig_note_finder import KeySignatureNoteFinder

"""
..module:: mmp_to_musicxml-documentation
"""

# future goals: somehow read in a single piano track and be able to figure out which notes should go on the bass staff lol.

# limitations: 
# - notes that extend beyond a measure will be truncated to fit within a measure
# - can't handle/identify TRIPLETS! :0 or anything smaller than 64th notes...
# - gotta normalize notes such that they're multiples of 8! i.e. if in LMMS you write down some notes using some smaller division like 1/64,
#   what looks like an eighth note (which should have a length of 24) might actually have a length of 25, which will throw everything off!

# ALSO IMPORTANT: if you're like me I tend to write all my string parts on one track, as well as for piano. unfortunately, this will break things 
# if trying to convert to xml. since there are so many different rhythms and notes you could possibly fit within a single measure, 
# before attempting to convert, the parts should be separated if you want more proper output (but doing so in LMMS is not too bad - just a bit of copying, pasting and scrubbing)

#note that a note element node from a mmp file looks like this (note the attributes):
#<note pan="-38" key="53" vol="59" pos="384" len="192"/>

class MMP_MusicXML_Converter:

	LMMS_MEASURE_LENGTH = 192
	
	# number of divisions per quarter note (see https://www.musicxml.com/tutorial/the-midi-compatible-part/duration/)
	NUM_DIVISIONS = "8"
	
	# these instruments will get treble clefs in the resulting xml
	INSTRUMENTS = set([
		"piano",
		"vibes",
		"viola",
		"violas",
		"violin",
		"violins",
		"french horn",
		"horn",
		"trumpet",
		"flute",
		"oboe",
		"clarinet",
		"guitar",
		"harp",
		"piccolo",
		"glockenspiel",
		"orchestra",
		"str",
		"strings",
		"marc str",
		"tenor sax",
		"tubular bells",
		"xylophone",
		"marimba",
	])
	
	# these instruments will get bass clefs in the resulting xml
	BASS_INSTRUMENTS = set([
		"bass",
		"cello",
		"basses",
		"cellos",
		"double bass",
		"double basses",
		"trombone",
		"tuba",
		"bassoon",
		"street bass",
		"timpani",
		"bass clarinet",
		"contrabass clarinet",
	])
	
	# https://en.wikipedia.org/wiki/General_MIDI
	MIDI_TABLE = {
		"piano": 1, # acoustic grand
		"harpsichord": 7,
		"celesta": 9,
		"glockenspiel": 10,
		"vibraphone": 12,
		"marimba": 13,
		"xylophone": 14,
		"tubular bells": 15,
		"violin": 41,
		"viola": 42,
		"cello": 43,
		"double bass": 44, # contrabass
		"harp": 47,
		"timpani": 48,
		"trumpet": 57,
		"trombone": 58,
		"tuba": 59,
		"horn": 61, # fr horn
		"oboe": 69,
		"bassoon": 71,
		"clarinet": 72,
		"piccolo": 73,
		"flute": 74,
	}
	
	NOTES = {
		0: "C",
		1: "C#",
		2: "D",
		3: "D#",
		4: "E",
		5: "F",
		6: "F#",
		7: "G",
		8: "G#",
		9: "A",
		10: "A#",
		11: "B",
	}

	# these are the true lengths of each note type.
	# for example, a 16th note has a length of 12
	# these numbers are based on note lengths in LMMS.
	NOTE_TYPE = {
		"whole": 192,
		"half": 96,
		"quarter": 48,
		"eighth": 24,
		"16th": 12,
		"32nd": 6,
		"64th": 3,
	}

	# these are the note types that should be used when given a certain length 
	# if no length perfectly matches, then the closest match is the one to use
	# note: these numbers are based on note lengths in LMMS!
	# this is too restrictive? 168 should really be a double dotted half note and 144 a dotted half??
	NOTE_LENGTHS = {
		192: "whole",
		168: "half",
		144: "half",
		96: "half",
		72: "quarter",
		48: "quarter",
		36: "eighth",
		24: "eighth",
		12: "16th",
		6: "32nd",
		3: "64th",
	}
	
	# available lengths for rests and their corresponding duration based on 32nd notes
	# note that this also depends on divisions!
	# assuming division = 8 here!
	# a duration of 1 = 1 32nd note
	REST_TYPES = {
		"32nd": "1",
		"16th": "2",
		"eighth": "4",
		"quarter": "8",
		"half": "16",
	}

	# properties for clef types 
	CLEF_TYPE = {
		"treble": {"sign": "G", "line": "2"},
		"bass": {"sign": "F", "line": "4"}
	}
	
	# for determining key signature element if specified
	# https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/fifths/
	FIFTHS = {
		"c": "0", # number of flats (negative num) or sharps (positive num)
		"g": "1",
		"d": "2",
		"a": "3",
		"e": "4",
		"b": "5",
		"fs": "6",
		"cs": "7",
		"f": "-1",
		"bb": "-2",
		"eb": "-3",
		"ab": "-4",
		"db": "-5",
		"gb": "-6",
		"cb": "-7",
	}

	# default values for time signature (4/4) 
	TIME_SIGNATURE_NUMERATOR = "4"
	TIME_SIGNATURE_DENOMINATOR = "4"
    
	# note checker to check if any instrument notes are out of the traditional range
	NOTE_CHECKER = None
	
	# note adjuster based on key signature if specified
	NOTE_ADJUSTER = None
	
	SPECIFIED_KEY_SIGNATURE = None
	
	opts = None
	minor = None

	def __init__(self, key_signature=None, params=None):
		logging.basicConfig(level=logging.DEBUG)
		
		if params:
			if 'opts' in params: self.opts = params['opts']
			if 'minor' in params: self.minor = params['minor']

		if self.opts and self.opts.check:
			logging.debug("note checking is on")
			self.NOTE_CHECKER = NoteChecker()
			
		if key_signature:
			if key_signature in self.FIFTHS:
				logging.debug(f"adjusting notes per key signature: {key_signature}")
				if self.minor: logging.debug(f"minor mode [{self.minor}]")
				self.NOTE_ADJUSTER = KeySignatureNoteFinder()
				self.SPECIFIED_KEY_SIGNATURE = key_signature
			else:
				logging.debug(f"unidentifiable key signature argument was given: {key_signature}")

	def find_closest_note_type(self, length: int) -> str:
		"""For a given length, find the closest note type (i.e. half, whole, quarter)
		
		 This function attemps to find the closest, largest length that's less than or equal to the given length 
		 returns the closest note type match (i.e. half, quarter, etc.)
		 
		 Arguments: 
			- length(int): length of a note 
			
		 Returns a string indicating the closest note length
		"""
		closest_length = None
		
		for note_length in sorted(self.NOTE_LENGTHS, reverse=True):
			if note_length <= length:
				return self.NOTE_LENGTHS[note_length]
					
		if closest_length == None:
			return self.NOTE_LENGTHS[3]

	def add_note(self, parent_node: ET.Element, note: ET.Element, is_chord=False, length_table=None) -> ET.Element:
		"""Add a new note
		
		 Can specify if adding a new note to a chord (which appends a chord element)
		 Can also supply a lengthTable, which maps the note positions to the smallest-length-note at each position
		 
		 Arguments:
			- parent_node (ElementTree element node): the parent node that the note should be added to 
			- note (ElementTree element node): a node representing a note given by the mmp file
			- is_chord (bool): specify if this note is part of a chord 
			- length_table (dict)
			
		 Returns a reference to the element node representing the note
		"""
		pitch = self.NOTES[int(note.attrib["key"]) % 12]
		position = int(note.attrib["pos"])
		new_note = ET.SubElement(parent_node, "note")
		
		# if note belongs to chord 
		if is_chord:
			new_chord = ET.SubElement(new_note, "chord")
		
		new_pitch = ET.SubElement(new_note, "pitch")
		new_step = ET.SubElement(new_pitch, "step")
		
		if self.NOTE_ADJUSTER:
			# might need to convert a sharp note to a flat note
			# depending on specified key signature
			if self.NOTE_ADJUSTER.need_to_convert(pitch, self.SPECIFIED_KEY_SIGNATURE):
				adjusted_note = self.NOTE_ADJUSTER.adjust_note_per_key_signature(pitch, self.SPECIFIED_KEY_SIGNATURE)
				
				# adjust octave as well if we adjusted a note to its enharmonic whose natural
				# note ends up in the next octave (e.g. B -> Cb). I think this only happens for B -> Cb?
				if adjusted_note == "Cb" and pitch == "B":
					note.attrib["key"] = str(int(note.attrib["key"]) + 12)
				
				# and then similarly for a C that should actually be a B# (e.g. if key signature is C#)
				if adjusted_note == "B#" and pitch == "C":
					note.attrib["key"] = str(int(note.attrib["key"]) - 12)
				
				pitch = adjusted_note
		
		new_step.text = str(pitch[0])
		
		if len(pitch) > 1 and pitch[1] == "#":
			# if pitch is a sharp note, e.g. "E#"
			new_alter = ET.SubElement(new_pitch, "alter")
			new_alter.text = "1"
		elif len(pitch) > 1 and pitch[1] == "b":
			# if pitch should be a flat note, e.g. "Bb"
			new_alter = ET.SubElement(new_pitch, "alter")
			new_alter.text = "-1"
		
		# calculate octave 
		octave = int(int(note.attrib["key"]) / 12) # basically floor(piano key number / 12)
		
		new_octave = ET.SubElement(new_pitch, "octave")
		new_octave.text = str(octave)
		
		# do some math to get the duration given length of note 
		note_length = int(note.attrib["len"])

		if length_table != None:
			# when would it be None?
			# note that the note length is actually the corrected length
			# this is because I'm not handling dotted notes right now so that if you use the actual length given by LMMS,
			# you're going to skip out on some rests and throw everything off 
			# instead take the note's original length but use NOTE_TYPE to get the corrected length
			note_length = self.NOTE_TYPE[self.find_closest_note_type(length_table[position])]
		
		new_duration = ET.SubElement(new_note, "duration")
		new_duration.text = str(int(note_length / 6))
		
		# need to identify the note type 
		new_type = ET.SubElement(new_note, "type")
		new_type.text = self.find_closest_note_type(note_length)
		return new_note

	def add_rest(self, parent_node: ET.Element, rest_type: str) -> ET.Element:
		"""Add a new rest of a specific type
		
		 See here for possible types: https://usermanuals.musicxml.com/MusicXML/Content/ST-MusicXML-note-type-value.htm
		 
		 Arguments:
			- parent_node (ElementTree element node): the parent node to add the rest to 
			- rest_type (str): type of note (i.e. eighth, 16th, etc.)
			
		 Returns a reference to the element node representing the rest 
		"""
		# you will need to figure out the duration given the type! i.e. 16th = duration of 2 if divisions is 8 
		# so if divisions = 8, then the smallest unit is 32nd notes, since 8 32nd notes go into 1 quarter note 
		new_note = ET.SubElement(parent_node, "note")
		new_rest = ET.SubElement(new_note, "rest")
		new_duration = ET.SubElement(new_note, "duration")
		
		# calculate the correct duration text depending on type 
		dur = self.REST_TYPES[rest_type] if rest_type in self.REST_TYPES else ""			
		new_duration.text = dur
		
		new_type = ET.SubElement(new_note, "type")
		new_type.text = rest_type
		return new_note 

	def get_rests(self, initial_distance: int) -> OrderedDict:
		"""Figure out types and number of rests needed given a length from one note to another 
		
		 Arguments:
			- initial_distance (int): the distance between 2 notes from the LMMS .mmp file
			
		 Returns an ordered dictionary that maps each type of rest to its quantity to add
		 This is so when traversing the dictionary you can get the smallest rest first to the largest rest.
		"""
		rests_to_add = OrderedDict()
		
		# how many whole rests? 
		num_whole_rests = initial_distance // self.LMMS_MEASURE_LENGTH
		rem_size = initial_distance - (num_whole_rests*self.LMMS_MEASURE_LENGTH)
		
		# how many quarter rests? 
		num_quarter_rests = int(rem_size/48)
		rem_size -= num_quarter_rests*48 
		
		# how many eighth rests?
		num_eighth_rests = int(rem_size/24)
		rem_size -= num_eighth_rests*24 
		
		# how many 16th rests?
		num_16th_rests = int(rem_size/12)
		rem_size -= num_16th_rests*12 
		
		# how many 32nd rests?
		num_32nd_rests = int(rem_size/6)
		rem_size -= num_32nd_rests*6 
		
		# how many 64th rests? only go up to 64 for now?
		num_64th_rests = int(rem_size/3)
		rem_size = rem_size - num_64th_rests*3 
		
		rests_to_add["64th"] = num_64th_rests
		rests_to_add["32nd"] = num_32nd_rests
		rests_to_add["16th"] = num_16th_rests
		rests_to_add["eighth"] = num_eighth_rests
		rests_to_add["quarter"] = num_quarter_rests
		rests_to_add["whole"] = num_whole_rests

		return rests_to_add 

	def create_measure(self, parent_node: ET.Element, measure_num: int) -> ET.Element:
		"""Create a measure node 
		
		 Arguments:
			- parent_node (ElementTree element node)
			- measure_num (int): the measure number
			
		 Returns a reference to a newly created measure node
		"""
		new_measure = ET.SubElement(parent_node, "measure")
		new_measure.set("number", str(measure_num))
		return new_measure

	def create_first_measure(
		self, 
		parent_node: ET.Element,
		measure_num: int,
		clef_type: str,
		is_rest=False
	) -> ET.Element:
		"""Create initial measure of the resulting MusicXML file. 
		 
		 Arguments:
			- parent_node (ElementTree element node)
			- measure_num (int): the measure number
			- clef_type (str): "treble" or "bass"
			- is_rest (bool): whether the first measure should be a whole rest
		 
		 Every first measure of an instrument needs some special properties like clef 
		 All first measures have an attribute section, but if it's a rest measure there are additional fields 
		 
		 Returns a reference to a newly created measure node
		"""
		first_measure = self.create_measure(parent_node, measure_num)
		new_measure_attributes = ET.SubElement(first_measure, "attributes")
		
		# for the first measure, we need to indicate divisions, clef, key
		# for divisions, this is how much a quarter note will be subdivided
		# so if you have only eighth notes as the smallest unit in your piece, 
		# use 2 if 16th is the smallest, use 4, etc. 
		# how to know this programatically though? iterate through all notes just to 
		# see first??? just go with 8 for now (so 32nd notes are the smallest unit)
		divisions = ET.SubElement(new_measure_attributes, "divisions")
		divisions.text = self.NUM_DIVISIONS
		
		key = ET.SubElement(new_measure_attributes, "key")
		fifths = ET.SubElement(key, "fifths")
		
		if self.SPECIFIED_KEY_SIGNATURE and self.SPECIFIED_KEY_SIGNATURE in self.FIFTHS:
			fifths.text = self.FIFTHS[self.SPECIFIED_KEY_SIGNATURE]
		else:
			fifths.text = "0"
		
		time = ET.SubElement(new_measure_attributes, "time")
		time_beats = ET.SubElement(time, "beats")
		time_beats.text = self.TIME_SIGNATURE_NUMERATOR
		time_beat_type = ET.SubElement(time, "beat-type")
		time_beat_type.text = self.TIME_SIGNATURE_DENOMINATOR 

		# on second thought, adding 2 staves may only be useful if your piano parts are single-tracked before processing.
		# if you go through the effort of separating the left and right hand parts into their own tracks,
		# then this would probably not be helpful. leaving this here as maybe something to revisit later.
		# if two_staves:
			# new_staves = ET.SubElement(new_measure_attributes, "staves")
			# new_staves.text = "2"
		
		new_clef = ET.SubElement(new_measure_attributes, "clef")
		clef_sign = ET.SubElement(new_clef, "sign")
		clef_sign.text = self.CLEF_TYPE[clef_type]["sign"] 
		clef_line = ET.SubElement(new_clef, "line")
		clef_line.text = self.CLEF_TYPE[clef_type]["line"]
		
		if is_rest:
			new_note = ET.SubElement(first_measure, "note")
			new_rest = ET.SubElement(new_note, "rest")
			new_rest.set("measure", "yes")
			new_duration = ET.SubElement(new_note, "duration")
			new_duration.text = str(int(self.TIME_SIGNATURE_NUMERATOR) * int(self.NUM_DIVISIONS))
			
		return first_measure 
		
	def add_rest_measure(self, parent_node: ET.Element, measure_num: int) -> ET.Element:
		"""Add a complete measure of rest 
		
		 Arguments:
			- parent_node (ElementTree element node)
			- measure_num (int)
			
		 Returns a reference to a newly created measure node
		"""
		new_rest_measure = ET.SubElement(parent_node, "measure")
		new_rest_measure.set("number", str(measure_num))
		
		# make sure to add rest element in 'note' section 
		new_note = ET.SubElement(new_rest_measure, "note")
		new_rest = ET.SubElement(new_note, "rest")
		new_rest.set("measure", "yes")
		new_duration = ET.SubElement(new_note, "duration")
		
		# should be beats * duration - here is 32 because 4 beats, each beat has 8 subdivisions 
		new_duration.text = str(
			int(self.TIME_SIGNATURE_NUMERATOR) * int(self.NUM_DIVISIONS)
		)

		return new_rest_measure

	def new_measure_check(self, curr_length: int) -> bool:
		"""Checks if a new measure should be added given the current length of notes in a measure so far.
		
		 Arguments:
			- curr_length (int): the current length of accumulated notes in a measure
		
		  The length passed should be a value given by create_length_table() so that currLength 
		  will always eventually be a value where mod (whatever the measure length is) is 0
		  
		 Returns True if a new measure should be added, False if not.  
		"""
		return (curr_length % self.LMMS_MEASURE_LENGTH) == 0
		
	def add_rests_for_length(self, size: int, curr_measure: ET.Element):
		""" Adds rests based on a given size
		
		Arguments:
			- size (int): the size of the section that should be filled with rests 
			- curr_measure (ElementTree element node)
		"""
		rests_to_add = self.get_rests(size)
		for rest_type in rests_to_add:
			for x in range(0, rests_to_add[rest_type]):
				self.add_rest(curr_measure, rest_type)

	def create_length_table(self, notes: List[ET.Element]) -> dict:
		"""Creates a dictionary mapping note positions in the LMMS .mmp file to what their lengths should be in the MusicXML file  
		
		 Arguments:
			- notes (list): list of ElementTree element nodes representing notes
		
		 Returns a dictionary
		"""
		length_table = {} 
		
		# also truncate some lengths as needed if they carry over to the next measure?
		# example: look at the 2nd-to-last and last notes. 372 + 48 > 384, but 384 is the next measure.
		# so therefore if we didn't have any other notes at that position except the one with length 48, 
		# the 2nd-to-last note's length should be truncated to 12, the smallest length at that position
		# that does not carry over to the next measure.
		#
		#  <note pan="0" key="67" vol="48" pos="372" len="48"/>
		#  <note pan="0" key="77" vol="48" pos="384" len="48"/> 
		#
		# we also have to truncate notes within the same measure
		# example: the 2nd note below happens before the 1st note ends.
		#
		#  <note pan="0" key="67" vol="97" pos="192" len="96"/>
		#  <note pan="0" key="60" vol="82" pos="216" len="48"/>
		#  <note pan="0" key="62" vol="87" pos="264" len="96"/>
		#
		# this scenario also:
		# the note at post 144 becomes a half note and makes the current measure too large by a quarter note 
		# pos: 144, len: 240, measure: 1
		# pos: 240, len: 144, measure: 2
		# this scenario is remedied by only updating the length table if a new smaller length is found for a position already in the table 
		
		next_measure_pos = self.LMMS_MEASURE_LENGTH
		for i in range(0, len(notes)):
			note = notes[i][0]
			position = int(note.attrib["pos"])
			length = int(note.attrib["len"])
			
			if position in length_table:
				if length < length_table[position]:
					length_table[position] = length
				
				# there might be an instance where we have at least 2 notes in the same position,
				# but they're the same length AND they should actually be truncated because they
				# spill over into another note like in the second if statement below (in the else block) so we need to check that here 
				if i < len(notes)-1 and ((length + position) > int(notes[i+1][0].attrib["pos"])) and position != int(notes[i+1][0].attrib["pos"]):
					next_note_pos = int(notes[i+1][0].attrib["pos"])
					
					# but the new length must be smaller in order to be updated 
					if next_note_pos - position < length_table[position]:
						length_table[position] = next_note_pos - position 
			else:
				curr_measure_pos = (notes[i][1]-1) * self.LMMS_MEASURE_LENGTH # notes[i][1]-1 is the measure number 
				next_measure_pos = curr_measure_pos + self.LMMS_MEASURE_LENGTH
				
				# we want to know if this current note carries over into the next measure 
				# to find out we can see if the current note's position plus its length 
				# is greater than the next measure's position (i.e. this note spills over into the next measure)
				curr_note_distance = position + length 

				if curr_note_distance > next_measure_pos:
					# truncate the note so that its length only goes up to the next measure's position 
					length = next_measure_pos - position
				
				if i < len(notes)-1:
					prev_note_pos = int(notes[i+1][0].attrib["pos"])
					if ((length + position) > prev_note_pos) and position != prev_note_pos:
						# similar to above, but checking if current note's length overlaps with the next note's position. 
						# if the current note ends after the next note starts, truncate the current note's length
						# the new length will be the difference between the next note's position and the current note's position
						# it's also important to check that this current note is not in the same position as the next note (which forms a chord)
						# we need this check because otherwise we might get a 0 for the length value 
						next_note_pos = int(notes[i+1][0].attrib["pos"])
						length = next_note_pos - position 
						#logging.debug(str(l) + ", l+p: " + str(l+p) )

				length_table[position] = length
				#logging.debug(lengthTable)
				
		return length_table 

	def convert_file(self, filepath: str):
		"""Does the converting from .mmp to MusicXML.
		"""
		file = filepath
		
		if ".mmp" not in file:
			raise ValueError("not an .mmp file!")
			
		# extract just the file's name 
		lastSlashIndex = file.rfind("/")
		extensionIndex = file.rfind(".mmp")
		outputFileName = file[(lastSlashIndex+1):extensionIndex]
			
		tree = ET.parse(file)
		root = tree.getroot()

		# get the time signature of the piece 
		self.TIME_SIGNATURE_NUMERATOR = str(root.find('head').attrib['timesig_numerator'])
		self.TIME_SIGNATURE_DENOMINATOR = str(root.find('head').attrib['timesig_denominator'])

		# get the master pitch. if it's not 0, we can alter the notes accordingly. 
		MASTER_PITCH = int(root.find('head').attrib['masterpitch'])

		if self.opts and self.opts.master:
			MASTER_PITCH = int(self.opts.master)
			logging.debug(f"MASTER_PITCH: {str(MASTER_PITCH)}")

		# LMMS measure length variable needs to be based on the time signature numerator 
		# a quarter note is always length 48 
		self.LMMS_MEASURE_LENGTH = self.NOTE_TYPE["quarter"] * int(self.TIME_SIGNATURE_NUMERATOR)
	
		logging.debug(file)
		logging.debug(f"LMMS_MEASURE_LENGTH: {str(self.LMMS_MEASURE_LENGTH)}")
		logging.debug(f"TIME SIGNATURE: {str(self.TIME_SIGNATURE_NUMERATOR)}/{str(self.TIME_SIGNATURE_DENOMINATOR)}")
		#logging.debug("Duration of a measure (with 32nd notes): " + str(int(TIME_SIGNATURE_NUMERATOR) * int(NUM_DIVISIONS)))

		# write a new xml file 
		new_file = open(outputFileName + ".xml", "w")

		# add the appropriate headers first 
		new_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
		new_file.write('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n')

		# create the general tree structure, then fill in accordingly
		score_partwise = ET.Element('score-partwise')

		# title of piece
		movement_title = ET.SubElement(score_partwise, 'movement-title')

		if self.opts and self.opts.title:
			movement_title.text = self.opts.title
			logging.debug (f"title: {movement_title.text}")
		else:
			movement_title.text = "title of piece goes here"

		# instrument track names
		if self.opts and self.opts.instruments:
			names = self.opts.instruments.split('+')
			logging.debug (f"tracks: {'|'.join(names)}")
		else:
			names = self.INSTRUMENTS.union(self.BASS_INSTRUMENTS)

		# list of the instrument parts 
		part_list = ET.SubElement(score_partwise, 'part-list')

		# then go through each instrument in the mmp file and add them to part-list 
		instrument_counter = 1
		for el in tree.iter(tag = 'track'):
			name = el.attrib['name']
			isMuted = el.attrib['muted'] == "1"
			inst_count = str(instrument_counter)
			
			if (name in names) and not isMuted:
				# need to also check if there are notes for this instrument. if it's an empty track, skip it
				if el.find("pattern") is None:
					continue
				
				new_part = ET.SubElement(part_list, "score-part")
				new_part.set('id', "P" + inst_count)
				
				new_part_name = ET.SubElement(new_part, "part-name")
				new_part_name.text = name
				
				new_part_name_abbr = ET.SubElement(new_part, "part-abbreviation")
				new_part_name_abbr.text = name[0:2] + "."
				
				# add midi instrument element
				# TODO: have this togglable via an argument when calling the script?
				instrumenttrack_element = el.find("instrumenttrack")
				instrument_pan = instrumenttrack_element.attrib['pan']
				instrument_vol = instrumenttrack_element.attrib['vol']
				instrument_pitch = instrumenttrack_element.attrib['pitch'] # this can be important if you want to take into account the pitch offset in LMMS
				
				score_instrument_el = ET.SubElement(new_part, "score-instrument")
				score_instrument_el.set('id', "P" + inst_count + "-I" + inst_count)
				inst_name_el = ET.SubElement(score_instrument_el, "instrument-name")
				inst_name_el.text = name
				
				midi_instrument_el = ET.SubElement(new_part, "midi-instrument")
				midi_instrument_el.set('id', "P" + inst_count + "-I" + inst_count)
				
				midi_program_el = ET.SubElement(midi_instrument_el, "midi-program")
				midi_program_el.text = str(self.MIDI_TABLE.get(name.lower(), 1)) # use piano by default if no match found in table
				
				volume_el = ET.SubElement(midi_instrument_el, "volume")
				volume_el.text = "78.7402"
				
				pan_el = ET.SubElement(midi_instrument_el, "pan")
				pan_el.text = str(instrument_pan)
				
				# move to next instrument
				instrument_counter += 1

		# now that the instruments have been declared, time to write out the notes for each instrument 
		# the xml file for a LMMS project might not actually have the notes in order for an instrument!!! 
		# notes in LMMS are separated in chunks called 'patterns' in the XML file (.mmp). each pattern has 
		# a position, so use that to sort the patterns in order. then write out the notes 
		
		instrument_counter = 1 	# reset instrument_counter for the next step

		# we need to keep track of each part - their part id node and the last measure num they had notes for. 
		# at the very end we need to make sure every part has the same number of measures 
		part_measures = {}

		# for each track element
		for el in tree.iter(tag = 'track'):
			name = el.attrib['name']
			is_muted = el.attrib['muted'] == "1"
			
			if (name in names) and not is_muted:
				# get the pattern chunks (which hold the notes)
				pattern_chunks = []
				for el2 in el.iter(tag = 'pattern'):
					pattern_chunks.append(el2)
				
				curr_measure = None
				pattern_notes = [] # list of tuple containing a note and its measure num, i.e. (note, measure)
				
				# concatenate all the patterns and get their notes all in one list 
				for i in range(0, len(pattern_chunks)):
					# get the position of the pattern. note that a pattern might not start at position 0!
					# if it doesn't start at 0 and it's the first pattern, or the current chunk doesn't start
					# where the previous chunk left off, then you need to make rest measures to fill in any gaps. 
					# another LMMS xml file property -> every measure is of length (time signature numerator * 48), so each measure's position 
					# is a multiple of that product 
					chunk = pattern_chunks[i].iter(tag = 'note')
					chunk_pos = int(pattern_chunks[i].attrib["pos"])
					measure_num = int(chunk_pos/self.LMMS_MEASURE_LENGTH) + 1 # patterns always start on a multiple of 192 
					
					for n in chunk:
						# because each note's position is relative to their pattern, each note's position should be their pattern pos + note pos 
						# but an important piece of information is what measure this note falls in.
						# we'll record the measure in a tuple along with a reference to the note, i.e. (noteReference, measureNumber)
						note_pos = int(n.attrib["pos"])			
						new_pos = chunk_pos + note_pos 
						n.set("pos", str(new_pos))
						
						# increment measure num if needed
						if new_pos >= (measure_num*self.LMMS_MEASURE_LENGTH):
							# if note is within the next measure over 
							if new_pos < ((measure_num+1)*self.LMMS_MEASURE_LENGTH):
								measure_num += 1
							else:
								# the newPos might actually be a few measures over, not just the next measure! 
								# need to add 1 because positions start at 0
								measure_num = (new_pos // self.LMMS_MEASURE_LENGTH) + 1
						
						pattern_notes.append((n, measure_num))
				
				# sort the notes in the list by position
				# remember that the elements are tuples => (note, the measure the note is in)
				pattern_notes = sorted(pattern_notes, key=lambda p: int(p[0].attrib["pos"]))

				# this is very helpful for checking notes 
				#if name == 'tuba':
				#	logging.debug("----- " + str(name) + " ------------------")
				#	for p in pattern_notes:
				#		logging.debug("pos: " + str(p[0].attrib["pos"]) + ", len: " + str(p[0].attrib["len"]) + ", measure: " + str(p[1]))
				#	logging.debug("-----------------------")
						
				notes = pattern_notes
				
				# if no notes (i.e. empty pattern), skip this instrument
				if len(notes) == 0:
					continue
				
				# for each valid instrument el, create a new part section that will hold its measures and their notes
				current_part = ET.SubElement(score_partwise, "part");
				current_part.set("id", "P" + str(instrument_counter))
					
				# find out what the smallest note length should be for stacked notes in a chord
				# this unfortunately means tied notes will be broken
				position_lengths = self.create_length_table(notes)
				
				# first create the first measure for this intrument. it might be a rest measure, 
				# or rest measures might need to be added first!
				first_note_pos = int(notes[0][0].attrib["pos"])
				first_note_measure_num = notes[0][1]

				if first_note_measure_num == 1:
					# if first note starts from the very beginning, create initial measure without any rests padding
					if name in self.BASS_INSTRUMENTS:
						curr_measure = self.create_first_measure(current_part, first_note_measure_num, "bass", is_rest=False)
					else:
						curr_measure = self.create_first_measure(current_part, first_note_measure_num, "treble", is_rest=False)
				else:			
					# add whole rests first 
					num_whole_rests = first_note_measure_num - 1
					
					for i in range(0, num_whole_rests):
						if i == 0:
							if name in self.BASS_INSTRUMENTS:
								self.create_first_measure(current_part, i+1, "bass", is_rest=True)
							else:
								self.create_first_measure(current_part, i+1, "treble", is_rest=True)
						else:
							self.add_rest_measure(current_part, i+1)
					
					curr_measure = self.create_measure(current_part, first_note_measure_num)
					
				last_measure_num = first_note_measure_num 
				
				# then go through the notes
				part_measures[current_part] = 0 # keep track of how many measures this instrument has 
				positions_seen = set()
				for k in range(0, len(notes)):
					note = notes[k][0]
					note_len = int(notes[k][0].attrib["len"])
					measure_num = notes[k][1]
					position = int(note.attrib["pos"])
					rem_measure_size = (measure_num * self.LMMS_MEASURE_LENGTH) - (position + self.NOTE_TYPE[self.find_closest_note_type(position_lengths[position])])
					
					# adjust the note based on master pitch 
					note.attrib["key"] = str(int(note.attrib["key"]) + MASTER_PITCH)
					
					# check if note is within normal range if needed
					if self.NOTE_CHECKER:
						note_name = self.NOTES[int(note.attrib["key"]) % 12]
						note_octave = int(int(note.attrib["key"]) / 12)
						self.NOTE_CHECKER.evaluate_note(name, note_name, note_octave, f"measure {measure_num}")
					
					# since the notes list contains tuples where tuple[0] is the note object, 
					# and tuple[1] is the measure the note should go in, we can use this info 
					if last_measure_num == measure_num:
						# add the note (but check to see if it belongs to a chord!)
						if position in positions_seen:	
							# this note is part of a chord 
							self.add_note(curr_measure, note, True, position_lengths)
						else:
							# add rests if needed based on previous note's position, then add the note 
							if k > 0:
								prev_note_pos = int(notes[k-1][0].attrib["pos"])
								rest_length = position - (prev_note_pos + self.NOTE_TYPE[self.find_closest_note_type(position_lengths[prev_note_pos])])
							else:
								rest_length = position - ((measure_num-1)*self.LMMS_MEASURE_LENGTH)
						
							self.add_rests_for_length(rest_length, curr_measure)
								
							positions_seen.add(position)
							self.add_note(curr_measure, note, False, position_lengths)
						
						# pad the rest of the measure with rests if needed (i.e. this is the last note of this measure)
						if (k < len(notes) - 1 and notes[k+1][1] > measure_num ) or (k == (len(notes) - 1)):
							self.add_rests_for_length(rem_measure_size, curr_measure)
					else:
						# need to create new measure(s), then add the note
						if k > 0:
							num_whole_rests = measure_num - last_measure_num - 1
							for i in range(0, num_whole_rests):
								self.add_rest_measure(current_part, notes[k-1][1]+i+1)
							
							# create the new measure to place the note 
							curr_measure = self.create_measure(current_part, measure_num)
							
							# add the note (but check to see if it belongs to a chord!)
							if position in positions_seen:	
								# make new note but add to a chord
								# no need to check if need to make a new measure because these notes are in a chord 
								self.add_note(curr_measure, note, True, position_lengths)
							else:
								# this is reached when adding the first note of a new measure 
								rest_length = position - ((measure_num-1)*self.LMMS_MEASURE_LENGTH)
								self.add_rests_for_length(rest_length, curr_measure)
								
								# then add the note 
								positions_seen.add(position)
								self.add_note(curr_measure, note, False, position_lengths)
								#logging.debug(str(restsToAdd))
								#logging.debug(positionLengths)
							
							# pad the rest of the measure with rests if needed if we're the last note in the measure or the whole piece
							# scenarios that could trigger this condition: one measure with a single note 
							if (k < len(notes)-1 and notes[k+1][1] > measure_num) or (k == (len(notes)-1)):
								self.add_rests_for_length(rem_measure_size, curr_measure)
							
					part_measures[current_part] = measure_num
					last_measure_num = measure_num
				
				instrument_counter += 1
				
		# still need to add whole rests to the end of each instrument so they all have the same number of measures total, 
		# otherwise a corrupt file will be reported (but it will still work, at least in MuseScore)!
		highest_num_measures = 0
		for part in part_measures:
			if part_measures[part] > highest_num_measures:
				highest_num_measures = part_measures[part]
				
		for part in part_measures:
			if part_measures[part] < highest_num_measures:
				for i in range(part_measures[part]+1, highest_num_measures+1):
					self.add_rest_measure(part, i)

		# write tree to file 
		# make sure to pretty-print because otherwise everything will be on one line
		data = minidom.parseString(ET.tostring(score_partwise, encoding="unicode")).toprettyxml(indent="    ")
		data = data.replace("<?xml version=\"1.0\" ?>", "") # toprettyxml adds a xml declaration, but I have it already written to the file
		new_file.write(data)
