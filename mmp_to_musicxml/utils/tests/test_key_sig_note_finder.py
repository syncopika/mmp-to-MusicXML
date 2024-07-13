import pytest 

from ..key_sig_note_finder import KeySignatureNoteFinder
    
def test_creation():
	key_sig_note_finder = KeySignatureNoteFinder()
	assert key_sig_note_finder is not None
    
def test_note_list_creation():
	key_sig_note_finder = KeySignatureNoteFinder(key_signature='d')
	note_list = key_sig_note_finder.get_note_list()
	assert len(note_list) == 86
	
def test_note_list():
	key_sig_note_finder = KeySignatureNoteFinder(key_signature='a')
	note_list = key_sig_note_finder.get_note_list()
	assert len(note_list) == 86
	
	# check A4 - A5
	a4 = note_list[57]
	as4 = note_list[58]
	b4 = note_list[59]
	c4 = note_list[60]
	
	assert a4['octave'] == 4
	assert a4['diatonic'] is True
	assert a4['degree'] == 1
	assert a4['note'] == 'A'
	
	assert as4['octave'] == 4
	assert as4['diatonic'] is False
	assert as4['degree'] == -1
	assert as4['note'] == 'A#'
	
	assert b4['octave'] == 4
	assert b4['diatonic'] is True
	assert b4['degree'] == 2
	assert b4['note'] == 'B'
	
	assert c4['octave'] == 4
	assert c4['diatonic'] is False
	assert c4['degree'] == -1
	assert c4['note'] == 'C'