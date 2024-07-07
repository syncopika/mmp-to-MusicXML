import pytest 

from ..key_sig_note_finder import KeySignatureNoteFinder

@pytest.fixture(scope="session")
def key_sig_note_finder():
	key_sig_note_finder = KeySignatureNoteFinder()
	yield key_sig_note_finder
    
def test_creation(key_sig_note_finder):
	assert key_sig_note_finder is not None
    
def test_sharp_note_adjustment(key_sig_note_finder):
	assert key_sig_note_finder.adjust_note_per_key_signature("A", "F") == "A"
	assert key_sig_note_finder.adjust_note_per_key_signature("A#", "F") == "Bb"
	assert key_sig_note_finder.need_to_convert_to_flat("A#", "F") == True
	
	assert key_sig_note_finder.adjust_note_per_key_signature("a", "f") == "A"
	assert key_sig_note_finder.adjust_note_per_key_signature("A#", "f") == "Bb"
	assert key_sig_note_finder.need_to_convert_to_flat("a#", "F") == True
	
	assert key_sig_note_finder.need_to_convert_to_flat("C#", "F") == False
	assert key_sig_note_finder.adjust_note_per_key_signature("C#", "F") == "C#"
	
	assert key_sig_note_finder.need_to_convert_to_flat("C#", "Db") == True
	assert key_sig_note_finder.adjust_note_per_key_signature("C#", "Db") == "Db"
	
	assert key_sig_note_finder.need_to_convert_to_flat("D#", "Bb") == True
	assert key_sig_note_finder.adjust_note_per_key_signature("D#", "Bb") == "Eb"