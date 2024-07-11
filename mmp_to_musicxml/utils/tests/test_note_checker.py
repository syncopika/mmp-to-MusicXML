import pytest 

from ..note_checker import NoteChecker

@pytest.fixture(scope="session")
def notechecker():
	checker = NoteChecker()
	yield checker
    
def test_creation(notechecker):
	assert notechecker is not None
    
def test_get_note_weight(notechecker):
    assert notechecker.get_note_weight("A") == 10
    assert notechecker.get_note_weight("C") == 1
    assert notechecker.get_note_weight("C#") == 2
    assert notechecker.get_note_weight("G#") == 9
    assert notechecker.get_note_weight("B") == 12
    
# TODO
# test case: min is A#2 and note is A#1. A#1 should be invalid
# test case: min is A#4, note is A4. A4 should be invalid
# test case: min is E3, note is B3. B3 should be valid b/c E -> F -> G -> A -> B -> C (next octave)
def test_evaluate_note(notechecker):
    assert notechecker.evaluate_note("clarinet", "A#", 3) is True
    assert notechecker.evaluate_note("clarinet", "D#", 3) is False
    assert notechecker.evaluate_note("clarinet", "D", 7) is False
    assert notechecker.evaluate_note("clarinet", "C", 5) is True
    assert notechecker.evaluate_note("clarinet", "F", 3) is True
    assert notechecker.evaluate_note("clarinet", "A", 3) is True
    assert notechecker.evaluate_note("clarinet", "B", 3) is True
    assert notechecker.evaluate_note("oboe", "A#", 2) is True
    assert notechecker.evaluate_note("oboe", "B", 3) is True
    assert notechecker.evaluate_note("oboe", "A", 5) is True
    assert notechecker.evaluate_note("oboe", "B", 2) is True
    assert notechecker.evaluate_note("oboe", "A", 2) is False
    assert notechecker.evaluate_note("oboe", "G", 2) is False