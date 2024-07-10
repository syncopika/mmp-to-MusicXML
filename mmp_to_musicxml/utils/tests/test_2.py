import pytest 

from ..key_sig_note_finder import KeySignatureNoteFinder
    
def test_creation():
	key_sig_note_finder = KeySignatureNoteFinder()
	assert key_sig_note_finder is not None
    
def test_note_list_creation():
	key_sig_note_finder = KeySignatureNoteFinder(key_signature='d')
	note_list = key_sig_note_finder.get_note_list()
	assert len(note_list) == 86