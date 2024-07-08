"""
for finding the corresponding enharmonic for a specific key signature given a note

"""
import logging

class KeySignatureNoteFinder:

	enharmonic_table = {
		'f#': 'Gb',
		'a#': 'Bb',
		'c#': 'Db',
		'g#': 'Ab',
		'd#': 'Eb',
		'e#': 'F',
		'b': 'Cb',
		'e': 'Fb',
		'c': 'B#',
		'f': 'E#',
	}

	key_signature_table = {
		'f': ['Bb'],
		'bb': ['Bb', 'Eb'],
		'eb': ['Eb', 'Ab', 'Bb'],
		'ab': ['Ab', 'Bb', 'Db', 'Eb'],
		'db': ['Gb', 'Ab', 'Db', 'Bb', 'Eb'],
		'gb': ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb'],
		'cb': ['Fb', 'Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb'],
		'fs': ['F#', 'G#', 'A#', 'C#', 'D#', 'E#'],
		'cs': ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#'],
	}

	def __init__(self):
		logging.basicConfig(level=logging.DEBUG)

	def adjust_note_per_key_signature(self, note: str, key_signature: str) -> str:
		key_sig = key_signature.lower()
		n = note.lower()
		
		# if desired key signature is one we need to make adjustments for
		# and the note is a sharp that might need to be flat
		# or the note is a natural that needs to be sharp
		if key_sig in self.key_signature_table and n in self.enharmonic_table:
			enharmonic = self.enharmonic_table[n]
			# check if this enharmonic is in the desired key signature
			if enharmonic in self.key_signature_table[key_sig]:
				return enharmonic
		return note.upper()
		
	def need_to_convert(self, note: str, key_signature: str) -> bool:
		key_sig = key_signature.lower()
		n = note.lower()
		
		# if desired key signature is one we need to make adjustments for
		# and the note is a sharp that might need to be flat
		# or the note is a natural that needs to be sharp
		if key_sig in self.key_signature_table and n in self.enharmonic_table:
			enharmonic = self.enharmonic_table[n]
			# check if this enharmonic is in the desired key signature
			if enharmonic in self.key_signature_table[key_sig]:
				return True
		return False
		
