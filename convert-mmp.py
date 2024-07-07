from mmp_to_musicxml.converter import MMP_MusicXML_Converter

import argparse

if __name__ == "__main__":

	parser = argparse.ArgumentParser(
				prog='MMP to MusicXML',
				description='Helps convert LMMS .mmp files to MusicXML')
	
	parser.add_argument('filename')
	parser.add_argument('-c', '--check', help='Check if any instrument notes fall out of the expected range (if applicable).', default=False, action='store_true') # check notes if any instrument notes fall out of expected range
	parser.add_argument('-k', '--key', help='Specify the key signature for the piece. Options are: c (default), g, d, a, e, b, f, bb, eb, ab, db, gb, cb.', default=None) # specify key signature for piece (default is key of C Major)
	
	args = parser.parse_args()
	
	# check notes of each instrument (if applicable) to catch any out-of-normal-range notes
	converter = MMP_MusicXML_Converter(check_notes=args.check, key_signature=args.key)
	
	converter.convert_file(args.filename)
