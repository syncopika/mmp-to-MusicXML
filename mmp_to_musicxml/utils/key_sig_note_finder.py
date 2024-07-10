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
		0: ["B#", "C"],
		1: ["C#", "Db"],
		2: ["D"],
		3: ["D#", "Eb"],
		4: ["E", "Fb"],
		5: ["E#", "F"],
		6: ["F#", "Gb"],
		7: ["G"],
		8: ["G#", "Ab"],
		9: ["A"],
		10: ["A#", "Bb"],
		11: ["B", "Cb"],
	}
	
	# table to record which enharmonics should be used for which key signatures
	KEY_SIGNATURE_TABLE = {
		'd': ['F#', 'C#'],
		'e': ['F#', 'G#', 'C#', 'D#'],
		'f': ['Bb'],
		'g': ['F#'],
		'a': ['C#', 'F#', 'G#'],
		'b': ['C#', 'D#', 'F#', 'G#', 'A#'],
		'bb': ['Bb', 'Eb'],
		'eb': ['Eb', 'Ab', 'Bb'],
		'ab': ['Ab', 'Bb', 'Db', 'Eb'],
		'db': ['Gb', 'Ab', 'Db', 'Bb', 'Eb'],
		'gb': ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb'],
		'cb': ['Fb', 'Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb'],
		'fs': ['F#', 'G#', 'A#', 'C#', 'D#', 'E#'],
		'cs': ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#'],
	}
	
	NUM_KEYS = 86 # 12 notes * 8 octaves
	
	NOTE_LIST = None

	KEY_SIGNATURE = ''

	def __init__(self, key_signature='c'):
		logging.basicConfig(level=logging.DEBUG)
		self.KEY_SIGNATURE = key_signature
		self.NOTE_LIST = []
		self.__calculate_note_list()

	def __calculate_note_list(self):
		# how far from the tonic note the diatonic notes in a scale are
		diatonic_note_offsets = set([0, 2, 4, 5, 7, 9, 11])
		
		degree = 1
		tonic_pos = self.NOTE_START_POSITIONS[self.KEY_SIGNATURE]
		offset = 0 - (12 - tonic_pos)
		dist_from_tonic = 0
		octave = 0
		
		# i represents the number of a piano key
		for i in range(offset, self.NUM_KEYS):
			if i < 0:
				dist_from_tonic += 1
				if dist_from_tonic > 11:
					dist_from_tonic = 0
				continue
			else:
				note_options = self.NOTES[i % 12]
				
				if dist_from_tonic in diatonic_note_offsets:
					self.NOTE_LIST.append({
						'diatonic': True,
						'degree': degree,
						'note': note_options,
						'octave': octave,
					})
					
					degree += 1
					
					if degree > 7:
						degree = 1
						octave += 1
				else:
					self.NOTE_LIST.append({
						'diatonic': False,
						'degree': degree,
						'note': note_options,
						'octave': octave
					})
					
				dist_from_tonic += 1
				if dist_from_tonic > 11:
					dist_from_tonic = 0

		#print(self.NOTE_LIST)
		
	def get_note_list(self) -> List[Dict]:
		return self.NOTE_LIST
		
	def get_note_based_on_key(self, key_num: int) -> str:
		return self.NOTE_LIST[key_num]
