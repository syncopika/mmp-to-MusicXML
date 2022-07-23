import pytest 

from ..note_checker import NoteChecker

@pytest.fixture(scope="session")
def notechecker():
	checker = NoteChecker()
	yield checker
    
def test_creation(notechecker):
	assert notechecker is not None
    
def test_evaluate_note(notechecker):
    assert notechecker.evaluate_note("clarinet", "A#", 3) is False
    assert notechecker.evaluate_note("clarinet", "D", 7) is False
    assert notechecker.evaluate_note("clarinet", "C", 5) is True
    assert notechecker.evaluate_note("clarinet", "F", 3) is True
    assert notechecker.evaluate_note("clarinet", "E#", 3) is True