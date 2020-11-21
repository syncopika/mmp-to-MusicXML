import pytest
import xml.etree.ElementTree as ET 
from xml.dom import minidom 

from ..converter import MMP_MusicXML_Converter

# create the converter object once and reuse across all tests
@pytest.fixture(scope="session")
def mmp_converter():
	converter = MMP_MusicXML_Converter()
	yield converter


def test_creation(mmp_converter):
	assert mmp_converter is not None
	assert mmp_converter.LMMS_MEASURE_LENGTH == 192

def test_find_closest_note_type(mmp_converter):
	assert mmp_converter.find_closest_note_type(192) == "whole"
	assert mmp_converter.find_closest_note_type(170) == "half"
	assert mmp_converter.find_closest_note_type(5) == "64th"

def test_add_note(mmp_converter):
	parent_node = ET.Element('node')
	note = ET.Element('note')
	note.set('len', 192)
	note.set('key', 53)
	note.set('pos', 384)
	mmp_converter.add_note(parent_node, note, False, None)
	
	count = 0
	for child in parent_node:
		count += 1
		assert child.text is None
		# need to verify that note node has pitch child node -> step child node  
		#                                   duration and type children nodes also 
		
	assert count == 1

def test_create_measure(mmp_converter):
	parent_node = ET.Element('node')
	mmp_converter.create_measure(parent_node, 1)
	
	count = 0
	for child in parent_node:
		count += 1
		assert child.get('number') == str(1)
		
	assert count == 1
	
def test_get_rests(mmp_converter):
	whole_rest_length = 192 # same length as a measure in LMMS
	rests = mmp_converter.get_rests(whole_rest_length)
	for rest_type in rests:
		rest_count = rests[rest_type]
		if rest_type == "whole":
			assert rest_count == 1
		else:
			assert rest_count == 0
			
	whole_rest_plus = 192+48
	rests = mmp_converter.get_rests(whole_rest_plus)
	for rest_type in rests:
		rest_count = rests[rest_type]
		if rest_type == "whole":
			assert rest_count == 1
		elif rest_type == "quarter":
			assert rest_count == 1
		else:
			assert rest_count == 0
			
	more_rests = 48+48+24+12+6
	rests = mmp_converter.get_rests(more_rests)
	for rest_type in rests:
		rest_count = rests[rest_type]
		if rest_type == "quarter":
			assert rest_count == 2
		elif rest_type == "eighth":
			assert rest_count == 1
		elif rest_type == "16th":
			assert rest_count == 1
		elif rest_type == "32nd":
			assert rest_count == 1
		else:
			assert rest_count == 0
