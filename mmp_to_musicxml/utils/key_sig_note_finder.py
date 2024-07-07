"""
find corresponding enharmonic for a specific key signature given a note

Note (pun intended) that since by default we assign sharps to any non-natural notes,
we only have to take into account the cases where a user wants to set a key signature that has flats
and adjust accordingly. 

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
	}

	# note we only care about flat key signatures
	key_signature_table = {
		'f': ['Bb'],
		'bb': ['Bb', 'Eb'],
		'eb': ['Eb', 'Ab', 'Bb'],
		'ab': ['Ab', 'Bb', 'Db', 'Eb'],
		'db': ['Gb', 'Ab', 'Db', 'Bb', 'Eb'],
		'gb': ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb'],
		'cb': ['Fb', 'Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb']
	}

	def __init__(self):
		logging.basicConfig(level=logging.DEBUG)

	def adjust_note_per_key_signature(self, note: str, key_signature: str) -> str:
		key_sig = key_signature.lower()
		n = note.lower()
		
		# if desired key signature is one we need to make adjustments for
		# and the note is a sharp that might need to be flat
		if key_sig in self.key_signature_table and n in self.enharmonic_table:
			enharmonic = self.enharmonic_table[n]
			# check if this enharmonic is in the desired key signature
			if enharmonic in self.key_signature_table[key_sig]:
				return enharmonic
		return note.upper()
		
	def need_to_convert_to_flat(self, note: str, key_signature: str) -> bool:
		key_sig = key_signature.lower()
		n = note.lower()
		
		# if desired key signature is one we need to make adjustments for
		# and the note is a sharp that might need to be flat
		if key_sig in self.key_signature_table and n in self.enharmonic_table:
			enharmonic = self.enharmonic_table[n]
			# check if this enharmonic is in the desired key signature
			if enharmonic in self.key_signature_table[key_sig]:
				return True
		return False
		
