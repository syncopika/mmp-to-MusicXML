import pytest
import os
import filecmp

from ..converter import MMP_MusicXML_Converter

def test_a():
	converter = MMP_MusicXML_Converter(key_signature='a')
	
	testfile = os.path.join(os.path.dirname(__file__), 'test_key_sig\\a.mmp')
	testfile_expected_output = os.path.join(os.path.dirname(__file__), 'test_key_sig/expected_output\\a.xml')
	output = os.path.join(os.path.dirname(__file__), 'test_key_sig\\a.xml')
	
	converter.convert_file(testfile)
	
	assert filecmp.cmp(output, testfile_expected_output, shallow=False) is True
	
	os.remove(output)
	
def test_d():
	converter = MMP_MusicXML_Converter(key_signature='d')
	
	testfile = os.path.join(os.path.dirname(__file__), 'test_key_sig\\d.mmp')
	testfile_expected_output = os.path.join(os.path.dirname(__file__), 'test_key_sig/expected_output\\d.xml')
	output = os.path.join(os.path.dirname(__file__), 'test_key_sig\\d.xml')
	
	converter.convert_file(testfile)
	
	assert filecmp.cmp(output, testfile_expected_output, shallow=False) is True
	
	os.remove(output)

def test_gb():
	converter = MMP_MusicXML_Converter(key_signature='gb')
	
	testfile = os.path.join(os.path.dirname(__file__), 'test_key_sig\\gb.mmp')
	testfile_expected_output = os.path.join(os.path.dirname(__file__), 'test_key_sig/expected_output\\gb.xml')
	output = os.path.join(os.path.dirname(__file__), 'test_key_sig\\gb.xml')
	
	converter.convert_file(testfile)
	
	assert filecmp.cmp(output, testfile_expected_output, shallow=False) is True
	
	os.remove(output)

def test_cb():
	converter = MMP_MusicXML_Converter(key_signature='cb')
	
	testfile = os.path.join(os.path.dirname(__file__), 'test_key_sig\\cb.mmp')
	testfile_expected_output = os.path.join(os.path.dirname(__file__), 'test_key_sig/expected_output\\cb.xml')
	output = os.path.join(os.path.dirname(__file__), 'test_key_sig\\cb.xml')
	
	converter.convert_file(testfile)
	
	assert filecmp.cmp(output, testfile_expected_output, shallow=False) is True
	
	os.remove(output)

def test_gb_chromatic():
	converter = MMP_MusicXML_Converter(key_signature='gb')
	
	testfile = os.path.join(os.path.dirname(__file__), 'test_key_sig\\gb-chromatic.mmp')
	testfile_expected_output = os.path.join(os.path.dirname(__file__), 'test_key_sig/expected_output\\gb-chromatic.xml')
	output = os.path.join(os.path.dirname(__file__), 'test_key_sig\\gb-chromatic.xml')
	
	converter.convert_file(testfile)
	
	assert filecmp.cmp(output, testfile_expected_output, shallow=False) is True
	
	os.remove(output)
	
def test_f_chromatic():
	converter = MMP_MusicXML_Converter(key_signature='f')
	
	testfile = os.path.join(os.path.dirname(__file__), 'test_key_sig\\f-chromatic.mmp')
	testfile_expected_output = os.path.join(os.path.dirname(__file__), 'test_key_sig/expected_output\\f-chromatic.xml')
	output = os.path.join(os.path.dirname(__file__), 'test_key_sig\\f-chromatic.xml')
	
	converter.convert_file(testfile)
	
	assert filecmp.cmp(output, testfile_expected_output, shallow=False) is True
	
	os.remove(output)


# TODO: add tests for the other keys :)