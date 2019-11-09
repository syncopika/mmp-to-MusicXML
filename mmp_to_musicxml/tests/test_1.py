from ..converter import MMP_MusicXML_Converter

import xml.etree.ElementTree as ET 
from xml.dom import minidom 

def test_creation():
	converter = MMP_MusicXML_Converter()
	assert converter is not None
	
def test_find_closest_note_type():
	converter = MMP_MusicXML_Converter()
	assert converter.find_closest_note_type(192) == "whole"
	assert converter.find_closest_note_type(170) == "half"
	assert converter.find_closest_note_type(5) == "64th"
	
def test_add_note():
	converter = MMP_MusicXML_Converter()
	parent_node = ET.Element('node')
	note = ET.Element('note')
	note.set('len', 192)
	note.set('key', 53)
	note.set('pos', 384)
	converter.add_note(parent_node, note, False, None)
	
	count = 0
	for child in parent_node:
		count += 1
		assert child.text is None
		# need to verify that note node has pitch child node -> step child node  
		#                                   duration and type children nodes also 
		
	assert count == 1

def test_create_measure():
	converter = MMP_MusicXML_Converter()
	parent_node = ET.Element('node')
	converter.create_measure(parent_node, 1)
	
	count = 0
	for child in parent_node:
		count += 1
		assert child.get('number') == str(1)
		
	assert count == 1
	
	

	