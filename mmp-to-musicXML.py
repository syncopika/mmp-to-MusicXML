# current goal: get as many notes as accurately as possible from LMMS to XML for import to MuseScore
# this script is meant to be a quick-and-dirty way to get at least a good portion of the music from an LMMS mmp file to music sheets 
# it's not going to provide a perfect or even mostly complete score, but hopefully should reduce the amount of work required to transcribe 
# music from LMMS's piano roll to say MuseScore. :) 

# future goals: somehow read in a single piano track and be able to figure out which notes should go on the bass staff lol.

# major bugs: 
# bass instrument notes should be adjusted/transposed!!!

# can't handle/identify TRIPLETS! :0 or 32nd notes...
# i.e. if you have a dotted eighth plus a 32nd note, that will throw everything off because the smallest rest type right now is 16th

# ALSO IMPORTANT: if you're like me I tend to write all my string parts on one track, as well as for piano. unfortunately, this will break things 
# if trying to convert to xml. since there are so many different rhythms and notes you could possibly fit wihtin a single measure, 
# before attempting to convert parts will have to be separated (but doing so in LMMS is not too bad - just a bit of copying, pasting and scrubbing)
from collections import OrderedDict
import xml.etree.ElementTree as ET 
from xml.dom import minidom  # https://stackoverflow.com/questions/28813876/how-do-i-get-pythons-elementtree-to-pretty-print-to-an-xml-file/28814053

tree = ET.parse('testfiles/funbgmXMLTESTsmall.mmp') #'testfiles/funbgmXMLTEST.mmp' #'testfiles/funbgmXMLTESTsmall.mmp'
root = tree.getroot()

LMMS_MEASURE_LENGTH = 192
INSTRUMENTS = {"piano", "bass", "vibes", "orchestra", "violin", "cello", "tuba", "trombone", "french horn", "horn", "trumpet", "flute", "oboe", "clarinet", "bassoon", "street bass"}
NOTES = {0:'C', 1:'C#',2:'D',3:'D#',4:'E',5:'F',6:'F#',7:'G',8:'G#',9:'A',10:'A#',11:'B'}
SIXTEENTH = "16th"
NOTE_TYPE = {192: "whole", 168: "half", 144: "half", 96: "half", 72: "quarter", 48: "quarter", 36: "eighth", 24: "eighth", 12: "16th", 6: "32nd", 3: "64th"} # this is too restrictive? 168 should really be a double dotted half note and 144 a dotted half??

### helpful functions ###
def getInstruments():
	pass
	
# for a given length, find the closest note type 
# this function attemps to find the closest, largest length that's less than or equal to the given length 
# returns the closest note type match (i.e. half, quarter, etc.)
def findClosestNoteType(length):
	
	closestLength = None
	
	for noteLength in sorted(NOTE_TYPE, reverse=True):
		if noteLength <= length:
			return NOTE_TYPE[noteLength]
				
	if closestLength == None:
		return NOTE_TYPE[6]

# add a new note 
# can specify if adding a new note to a chord (which appends a chord element)
# can also supply a lengthTable, which maps the note positions to the smallest-length-note at each position
def addNote(parentNode, note, isChord=False, lengthTable=None):

	pitch = NOTES[int(note.attrib["key"]) % 12]
	position = int(note.attrib["pos"])
	newNote = ET.SubElement(parentNode, "note")
	
	# if note belongs to chord 
	if isChord:
		newChord = ET.SubElement(newNote, "chord")
	
	newPitch = ET.SubElement(newNote, "pitch")
	newStep = ET.SubElement(newPitch, "step")
	newStep.text = str(pitch[0])
	
	if len(pitch) > 1 and pitch[1] == '#':
		newAlter = ET.SubElement(newPitch, "alter")
		newAlter.text = "1"
	
	# calculate octave 
	octave = int(int(note.attrib["key"]) / 12) # basically floor(piano key number / 12)
	newOctave = ET.SubElement(newPitch, "octave")
	newOctave.text = str(octave)
	
	# do some math to get the duration given length of note 
	noteLength = int(note.attrib["len"])

	if lengthTable != None:
		# when would it be None?
		noteLength = lengthTable[position]
	
	newDuration = ET.SubElement(newNote, "duration")
	newDuration.text = str(int(noteLength/6))
	
	# need to identify the note type 
	newType = ET.SubElement(newNote, "type")
	newType.text = findClosestNoteType(noteLength)
	
	return newNote
	
# add a new rest of a specific type
# see here for possible types: https://usermanuals.musicxml.com/MusicXML/Content/ST-MusicXML-note-type-value.htm
def addRest(parentNode, type):
	# you will need to figure out the duration given the type! i.e. 16th = duration of 2 if divisions is 8 
	# right now we're assuming 16th rests only!!!
	newNote = ET.SubElement(parentNode, "note")
	newRest = ET.SubElement(newNote, "rest")
	newDuration = ET.SubElement(newNote, "duration")
	newDuration.text = "2" # 2 32nd notes = 1 16th note 
	newType = ET.SubElement(newNote, "type")
	newType.text = type
	return newNote 

	
# figure out types and number of rests needed given a length from one note to another 
def getRests(initialDistance):

	restsToAdd = OrderedDict()
	
	# how many whole rests? 
	numWholeRests = int(initialDistance/192)
	remSize = initialDistance - numWholeRests*192 
	
	# how many quarter rests? 
	numQuarterRests = int(remSize/48)
	remSize = remSize - numQuarterRests*48 
	
	# how many eighth rests?
	numEighthRests = int(remSize/24)
	remSize = remSize - numEighthRests*24 
	
	# how many 16th rests?
	num16thRests = int(remSize/12)
	remSize = remSize - num16thRests*12 
	
	# how many 32nd rests?
	num32ndRests = int(remSize/6)
	remSize = remSize - num32ndRests*6 
	
	# how many 64th rests? only go up to 64 for now?
	num64thRests = int(remSize/3)
	remSize = remSize - num64thRests*3 
	
	restsToAdd['whole'] = numWholeRests
	restsToAdd['quarter'] = numQuarterRests
	restsToAdd['eighth'] = numEighthRests
	restsToAdd['16th'] = num16thRests
	restsToAdd['32nd'] = num32ndRests
	restsToAdd['64th'] = num64thRests
	
	return restsToAdd 


# create a measure node 
def createMeasure(parentNode, measureCounter):
	newMeasure = ET.SubElement(parentNode, "measure")
	newMeasure.set("number", str(measureCounter))
	return newMeasure 
	
# create initial measure 
# every first measure of an instrument needs some special properties like clef 
# all first measures have an attribute section, but if it's a rest measure there are additional fields 
def createFirstMeasure(parentNode, measureCounter, isRest=False):
	
	firstMeasure = createMeasure(currentPart, measureCounter)
	
	newMeasureAttributes = ET.SubElement(firstMeasure, "attributes")
	
	# for the first measure, we need to indicate divisions, clef, key
	
	# for divisions, this is how much a quarter note will be subdivided
	# so if you have only eighth notes as the smallest unit in your piece, 
	# use 2 if 16th is the smallest, use 4, etc. 
	# how to know this programatically though? iterate through all notes just to 
	# see first??? just go with 8 for now (so 32nd notes are the smallest unit)
	divisions = ET.SubElement(newMeasureAttributes, "divisions")
	divisions.text = "8"
	
	key = ET.SubElement(newMeasureAttributes, "key")
	fifths = ET.SubElement(key, "fifths")
	fifths.text = "0"
	
	time = ET.SubElement(newMeasureAttributes, "time")
	timeBeats = ET.SubElement(time, "beats")
	timeBeats.text = "4" # get this information from the top of the mmp file!
	timeBeatType = ET.SubElement(time, "beat-type")
	timeBeatType.text = "4" # get this information from the top of the mmp file!

	# this needs to be changed depending on instrument!!
	newClef = ET.SubElement(newMeasureAttributes, "clef")
	clefSign = ET.SubElement(newClef, "sign")
	clefSign.text = "G" 
	clefLine = ET.SubElement(newClef, "line")
	clefLine.text = "2"
	
	if isRest:
		newNote = ET.SubElement(firstMeasure, "note")
		newRest = ET.SubElement(newNote, "rest")
		newRest.set("measure", "yes")
		newDuration = ET.SubElement(newNote, "duration")
		newDuration.text = "32"
		
	return firstMeasure 
	
# add a complete measure of rest 
def addRestMeasure(parentNode, measureCounter):
	newRestMeasure = ET.SubElement(parentNode, "measure")
	#newRestMeasure.set("implicit", "yes")
	newRestMeasure.set("number", str(measureCounter))
	
	# make sure to add rest element in 'note' section 
	newNote = ET.SubElement(newRestMeasure, "note")
	newRest = ET.SubElement(newNote, "rest")
	newRest.set("measure", "yes")
	newDuration = ET.SubElement(newNote, "duration")
	newDuration.text = "32" # should be beats * duration - here is 32 because 4 beats, each beat has 8 subdivisions 

	return newRestMeasure # return a reference to the newly created measure node 

# checks if a new measure should be added given the current length of notes
# the length passed should be calculated by createLengthTable() so that currLength will always eventually be a value where mod 192 is 0
def newMeasureCheck(currLength):
	return currLength%LMMS_MEASURE_LENGTH == 0
	
# creates a new measure and returns a reference to it 
def addNewMeasure(parentNode, measureNum):
	currMeasure = ET.SubElement(parentNode, "measure")
	currMeasure.set("number", str(measureNum))
	return currMeasure 

# takes list of notes 
# returns what the length of each note at each position should be 
def createLengthTable(notes):
	lengthTable = {} 
	
	# also truncate some lengths as needed if they carry over to the next measure?
	# example: look at the 2nd-to-last and last notes. 372 + 48 > 384, but 384 is the next measure.
	# so therefore if we didn't have any other notes at that position except the one with length 48, 
	# the 2nd-to-last note's length should be truncated to 12, the smallest length at that position
	# that does not carry over to the next measure.
	#
	#  <note pan="0" key="53" vol="36" pos="336" len="24"/>
	#  <note pan="0" key="60" vol="36" pos="372" len="12"/>
	#  <note pan="0" key="50" vol="36" pos="372" len="12"/>
	#  <note pan="0" key="79" vol="48" pos="372" len="48"/>
	#  <note pan="0" key="67" vol="48" pos="372" len="48"/> <=
	#  <note pan="0" key="77" vol="48" pos="384" len="48"/> <=
	#
	# we also have to truncate notes within the same measure
	# example: the 2nd note below happens before the 1st note ends.
	#
	#  <note pan="0" key="67" vol="97" pos="192" len="96"/>
    #  <note pan="0" key="60" vol="82" pos="216" len="48"/>
    #  <note pan="0" key="62" vol="87" pos="264" len="96"/>
    #  <note pan="0" key="59" vol="82" pos="288" len="96"/>
    #  <note pan="0" key="55" vol="82" pos="288" len="96"/>
	
	nextMeasurePos = LMMS_MEASURE_LENGTH
	for i in range(0, len(notes)):
		note = notes[i][0]
		p = int(note.attrib["pos"])
		l = int(note.attrib["len"])
		if p in lengthTable:
			if l < lengthTable[p]:
				lengthTable[p] = l 
		else:
			# if we have a note that carries over to the next measure, we need to truncate it
			if i < len(notes)-1 and p != int(notes[i+1][0].attrib["pos"]):
				
				currMeasurePos = (notes[i][1]-1)*LMMS_MEASURE_LENGTH
				nextMeasurePos = currMeasurePos + LMMS_MEASURE_LENGTH
				
				# we want to know if this current note carries over into the next measure 
				# to find out we can see if the current note's position plus its length is greater than the next measure's position 
				currNoteDistance = p + l 

				#print("currNoteDistance: " + str(currNoteDistance) + " nextMeasurePos: " + str(nextMeasurePos))
				if currNoteDistance > nextMeasurePos:
					# truncate the note 
					l = nextMeasurePos - p  
					print("truncated note that went over to next measure " + str(notes[i][1]+1) + ". new length: " + str(l))
					
				elif ((l + p) > int(notes[i+1][0].attrib["pos"])):
					# similar to above, but checking if current note's length overlaps with the next note's position. 
					# if the current note ends after the next note starts, truncate the current note's length
					# the new length will be the difference between the next note's position and the current note's position
					nextNotePos = int(notes[i+1][0].attrib["pos"])
					l = nextNotePos - p 
					#print(str(l) + ", l+p: " + str(l+p) )
			
			lengthTable[p] = l
		
	return lengthTable 

	
#print(root.attrib)

# write a new xml file 
# https://stackabuse.com/reading-and-writing-xml-files-in-python/

newFile = open("newxmltest.xml", "w")

# add the appropriate headers first 
newFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
newFile.write('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n')

# create the general tree structure, then fill in accordingly
scorePartwise = ET.Element('score-partwise')

# title of piece
movementTitle = ET.SubElement(scorePartwise, 'movement-title')
movementTitle.text = "title of piece goes here"

# list of the instrument parts 
partList = ET.SubElement(scorePartwise, 'part-list')

# then go through each instrument in the mmp file and add them to part-list 
instrumentCounter = 1
for el in tree.iter(tag = 'track'):
	name = el.attrib['name']
	if name in INSTRUMENTS:
		newPart = ET.SubElement(partList, "score-part")
		newPart.set('id', "P" + str(instrumentCounter))
		instrumentCounter += 1
		
		newPartName = ET.SubElement(newPart, "part-name")
		newPartName.text = name;


# now that the instruments have been declared, time to write out the notes for each instrument 
# for each instrument, we need to write out each measure by noting the properties of each measure
# then we write out each note in each measure 
# potential problems:
# the xml file for a LMMS project might not actually have the notes in order for an instrument!!! 
# notes in LMMS are separated in chunks called 'patterns' in the XML file (.mmp). each pattern has 
# a position, so use that to sort the patterns in order. then write out the notes 
instrumentCounter = 1

# for each track element
for el in tree.iter(tag = 'track'):

	name = el.attrib['name']
	
	if name in INSTRUMENTS:
		
		# for each valid instrument el, create a new part section that will hold its measures and their notes
		currentPart = ET.SubElement(scorePartwise, "part");
		currentPart.set("id", "P" + str(instrumentCounter))
		
		# get the pattern chunks (which hold the notes)
		patternChunks = []
		for el2 in el.iter(tag = 'pattern'):
			patternChunks.append(el2)
		
		measureCounter = 1
		currLength = 0
		currMeasure = None
		patternNotes = []
		
		# concatenate all the patterns and get their notes all in one list 
		for i in range(0, len(patternChunks)):
			# get the position of the pattern. note that a pattern might not start at position 0!
			# if it doesn't start at 0 and it's the first pattern, or the current chunk doesn't start
			# where the previous chunk left off, then you need to make rest measures to fill in any gaps. 
			# another LMMS xml file property -> every measure is of length 192, so each measure's position 
			# is a multiple of 192 
			chunk = patternChunks[i].iter(tag = 'note')
			chunkPos = int(patternChunks[i].attrib["pos"])
			measureNum = int(chunkPos / 192) + 1 # patterns always start on a multiple of 192 
			
			for n in chunk:
				# because each note's position is relative to their pattern, each note's position should be their pattern pos + note pos 
				# but an important piece of information is what measure this note falls in. we can find out what measure this note is in 
				# by first getting the chunk's position and dividing it by 192 -> this gets us the starting measure number of the chunk 
				# we can also know what measure the chunk ends at given its length (I don't think we need this info though for this)
				# so then for each note in the chunk, we keep a counter that accumulates note lengths seen so far 
				# as soon as that counter equals or exceeds 192, we reset it to 0 and increment the measure count 
				# we'll record the measure in a tuple along with a reference to the note, i.e. (noteReference, measureNumber)
				notePos = int(n.attrib["pos"])			
				newPos = chunkPos + notePos 
				n.set("pos", str(newPos))
				
				# increment measure num if needed 		
				if newPos >= (measureNum*LMMS_MEASURE_LENGTH):
					measureNum += 1
				
				patternNotes.append((n, measureNum))
					
		# sort the notes in the list by position
		# remember that the elements are tuples => (note, the measure note is in)
		patternNotes = sorted(patternNotes, key=lambda p : int(p[0].attrib["pos"]))

		#for p in patternNotes:
		#	print("pos: " + str(p[0].attrib["pos"]) + ", len: " + str(p[0].attrib["len"]) + ", measure: " + str(p[1]))
		#print("---------------")
			
		notes = patternNotes 
		positionsSeen = set()
			
		# find out what the smallest note length should be for stacked notes in a chord
		# this unfortunately means tied notes will be broken
		positionLengths = createLengthTable(notes)
		#print(positionLengths)
		
		# first create the first measure for this intrument. it might be a rest measure, 
		# or rest measures might need to be added first!
		# look at the first note to know what to do
		# make sure currMeasure variable is set to the first measure that has a note!
		firstNotePos = int(notes[0][0].attrib["pos"])
		if firstNotePos == 0:
			# if first note starts from the very beginning
			currMeasure = createFirstMeasure(currentPart, measureCounter, False)
			measureCounter += 1
		else:
		
			# how many rests to add before first note 
			print(getRests(firstNotePos))
		
			# add full rest measures first if needed 
			numRestMeasures = int(firstNotePos / LMMS_MEASURE_LENGTH)
			#print("num rest measures: " + str(numRestMeasures))
			for m in range(0, numRestMeasures):
				if m == 0:
					createFirstMeasure(currentPart, measureCounter, True)
					measureCounter += 1
				else:
					addRestMeasure(currentPart, measureCounter)
					measureCounter += 1
			
			numRestsToAdd = int((firstNotePos%LMMS_MEASURE_LENGTH)/12)#int(end / 12) # divide by 12 = number of 16th rests to add. THIS IS PROBABLY A BAD IDEAAAAA
			#print("num rests to add: " + str(numRestsToAdd))
			
			# then add individual rests as needed 
			for l in range(0, numRestsToAdd):
				if newMeasureCheck(currLength):
					currMeasure = addNewMeasure(currentPart, measureCounter)
					measureCounter += 1 
					currLength = 0		
				addRest(currMeasure, SIXTEENTH)
				currLength += 12 
			
			if newMeasureCheck(currLength):
				currMeasure = addNewMeasure(currentPart, measureCounter)
				measureCounter += 1 
				currLength = 0
				
	
		# then go through the notes
		for k in range(0, len(notes)):
		
			note = notes[k][0]
			
			# even within a pattern you could have the first note start at a position that's not 0. 
			# so we need to account for that too 
			# remember that position here is relative to the pattern. so if the first note in a pattern 
			# starts at the beginning of the pattern, its position is 0.
			position = int(note.attrib["pos"])
			pitch = NOTES[int(note.attrib["key"]) % 12]
			
			if position in positionsSeen:	
				# make new note but add to a chord
				# no need to check if need to make a new measure because these notes are in a chord 
				addNote(currMeasure, note, True, positionLengths)
				
				# for this, don't increment currLength!!
				continue		
			else:
				positionsSeen.add(position)
		
			if k == 0:
				# the first note of the measure 
				addNote(currMeasure, note, False, positionLengths)
				
				# increment length 
				currLength += positionLengths[position] 			
			else:
				# check for gaps, add rests if needed. don't forget to increment length accordingly!
				prevNotePos = int(notes[k-1][0].attrib["pos"])
				prevNoteLen = positionLengths[prevNotePos] # use the length as given in positionLengths for the previous position!
				
				if int(note.attrib["pos"]) != (prevNotePos + prevNoteLen):
				
					# we have a gap - need to add in some rests 
					# add full rest measures if needed, then calculate individual rests 
					numRestMeasures = int((position - (prevNotePos + prevNoteLen)) / 192) #int(firstNotePos / LMMS_MEASURE_LENGTH)
					for m in range(0, numRestMeasures):
							addRestMeasure(currentPart, measureCounter)
							measureCounter += 1
					
					numRestsToAdd = int(((position - (prevNotePos + prevNoteLen))%192)/12) #int((firstNotePos%LMMS_MEASURE_LENGTH)/12)
					
					# then add individual rests as needed 
					for l in range(0, numRestsToAdd):
						if newMeasureCheck(currLength):
							currMeasure = addNewMeasure(currentPart, measureCounter)
							measureCounter += 1 
							currLength = 0		
						addRest(currMeasure, SIXTEENTH)
						currLength += 12 

					# then add the note 
					if newMeasureCheck(currLength):
						currMeasure = addNewMeasure(currentPart, measureCounter)
						measureCounter += 1 
						currLength = 0
					addNote(currMeasure, note, False, positionLengths)
					
					# increment length 
					currLength += positionLengths[position]
						
				else:
					# just add the note
					if newMeasureCheck(currLength):
						currMeasure = addNewMeasure(currentPart, measureCounter)
						measureCounter += 1 
						currLength = 0
					addNote(currMeasure, note, False, positionLengths)
					
					# increment length 
					currLength += positionLengths[position]
				
		instrumentCounter += 1
				
# write tree to file 
# make sure to pretty-print because otherwise everything will be on one line
data = minidom.parseString(ET.tostring(scorePartwise, encoding="unicode")).toprettyxml(indent="    ")
data = data.replace("<?xml version=\"1.0\" ?>", "") # toprettyxml adds a xml declaration, but I have it already written to the file
newFile.write(data)

#for el in tree.iter(tag = 'track'):
#	print(el.attrib['name'])