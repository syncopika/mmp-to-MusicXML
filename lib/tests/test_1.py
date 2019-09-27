from ..mmp_to_musicXML import MMP_MusicXML_Converter

def test_creation():
	converter = MMP_MusicXML_Converter()
	assert converter is not None