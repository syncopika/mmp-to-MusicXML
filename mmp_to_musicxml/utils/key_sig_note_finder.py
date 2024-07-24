"""
for getting the right notes given a key signature

"""
import logging
from typing import List, Dict

class KeySignatureNoteFinder:
	
	# piano key positions
	NOTE_START_POSITIONS = {
		"c": 0,
		"cs": 1,
		"db": 1,
		"d": 2,
		"ds": 3,
		"eb": 3,
		"e": 4,
		"f": 5,
		"fs": 6,
		"gb": 6,
		"g": 7,
		"gs": 8,
		"ab": 8,
		"a": 9,
		"as": 10,
		"bb": 10,
		"cb": 11,
		"b": 11,
	}
	
	# the possible notes + enharmonics
	NOTES = {
		0: ["C", "B#"],
		1: ["C#", "Db"],
		2: ["D", "C##"],
		3: ["D#", "Eb"],
		4: ["E", "Fb"],
		5: ["F", "E#"],
		6: ["F#", "Gb"],
		7: ["G", "F##"],
		8: ["G#", "Ab"],
		9: ["A", "G##"],
		10: ["A#", "Bb"],
		11: ["B", "Cb"],
	}
	
	# table to record which enharmonics should be used for which key signatures (including their relative melodic minors)
	KEY_SIGNATURE_TABLE = {
		'c': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
		'd': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
		'e': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#', 'B#'],
		'f': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E'],
		'g': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
		'a': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#', 'E#'],
		'b': ['C#', 'D#', 'F#', 'G#', 'A#', 'E#', 'F##'],
		'bb': ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A'],
		'eb': ['Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D'],
		'ab': ['Ab', 'Bb', 'C', 'Db', 'Eb', 'F', 'G'],
		'db': ['Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb', 'C'],
		'gb': ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F'],
		'cb': ['Fb', 'Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb'],
		'fs': ['F#', 'G#', 'A#', 'C#', 'D#', 'E#', 'B#', 'C##'],
		'cs': ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#', 'F##', 'G##'],
	}
	
	NUM_KEYS = 86 # 12 notes * 8 octaves
	
	NOTE_LIST = None

	KEY_SIGNATURE = ''
	
	# how far from the tonic note the diatonic notes in a scale are
	DIATONIC_OFFSETS = [0, 2, 4, 5, 7, 9, 11]

	def __init__(self, key_signature='c'):
		logging.basicConfig(level=logging.DEBUG)
		self.KEY_SIGNATURE = key_signature
		self.NOTE_LIST = []
		self.__calculate_note_list()

	def __calculate_note_list(self):
		tonic_pos = self.NOTE_START_POSITIONS[self.KEY_SIGNATURE]
		offset = 0 - (12 - tonic_pos)
		dist_from_tonic = 0
		octave = -1
		
		# i represents the number of a piano key
		for i in range(offset, self.NUM_KEYS + 1):
			if i < 0:
				dist_from_tonic += 1
				if dist_from_tonic > 11:
					dist_from_tonic = 0
				continue
			else:
				note_candidates = self.NOTES[i % 12]
				
				note = note_candidates[0]
				
				if self.KEY_SIGNATURE in self.KEY_SIGNATURE_TABLE:
					# find right enharmonic based on key signature
					for candidate in note_candidates:
						if candidate in self.KEY_SIGNATURE_TABLE[self.KEY_SIGNATURE]:
							note = candidate
				
				if dist_from_tonic in self.DIATONIC_OFFSETS:
					self.NOTE_LIST.append({
						'diatonic': True,
						'degree': self.DIATONIC_OFFSETS.index(dist_from_tonic) + 1,
						'note': note,
						'octave': octave,
					})
				else:
					self.NOTE_LIST.append({
						'diatonic': False,
						'degree': -1, # do non-diatonic notes have degree?
						'note': note,
						'octave': octave
					})
					
				dist_from_tonic += 1
				if dist_from_tonic > 11:
					dist_from_tonic = 0
					octave += 1

		#print(self.NOTE_LIST)
		
	def get_note_list(self) -> List[Dict]:
		return self.NOTE_LIST
		
	def get_note_based_on_key(self, key_num: int) -> str:
		return self.NOTE_LIST[key_num]
