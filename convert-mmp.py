from mmp_to_musicxml.converter import MMP_MusicXML_Converter

import sys

if __name__ == "__main__":
	
	converter = MMP_MusicXML_Converter()
	
	file = 'testfiles/080415pianobgm3popver.mmp'
	if len(sys.argv) > 1:
		file = sys.argv[1]
			
	converter.convert_file(file)