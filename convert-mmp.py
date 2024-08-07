from mmp_to_musicxml.converter import MMP_MusicXML_Converter

import argparse

if __name__ == "__main__":

	# allow user to pick a minor key for key signature
	# thanks to @nicolai-rostov - https://github.com/syncopika/mmp-to-MusicXML/issues/7#issuecomment-2212604213
	minor_to_major_map = {
		"abm":  "cb",
		"ebm":  "gb",
		"bbm":  "db",
		"fm":   "ab",
		"cm":   "eb",
		"gm":   "bb",
		"dm":   "f",
		"am":   "c",
		"em":   "g",
		"bm":   "d",
		"fsm":  "a",
		"csm":  "e",
		"gsm":  "b",
		"dsm":  "fs",
		"asm":  "cs",
	}

	parser = argparse.ArgumentParser(
				prog='MMP to MusicXML',
				description='Helps convert LMMS .mmp files to MusicXML')
	
	parser.add_argument('filename')
	parser.add_argument('-c', '--check', help='Check if any instrument notes fall out of the expected range (if applicable).', default=False, action='store_true') # check notes if any instrument notes fall out of expected range
	parser.add_argument('-k', '--key', help=f'Specify the key signature for the piece. Options are: c (default), g, d, a, e, b, f, bb, eb, ab, db, gb, cb, fs, cs. You can also pass in a minor key: {", ".join(minor_to_major_map.keys())}.', default=None) # specify key signature for piece (default is key of C Major)
	parser.add_argument('-m', '--master', metavar='i', help='Set master pitch')
	parser.add_argument('-t', '--title', metavar='str', help='Set piece title')
	parser.add_argument('-i', '--instruments', metavar='str', help='Select instrument tracks using the plus sign (+) as list separator: violin+cello')
	
	args = parser.parse_args()
	
	if args.key in minor_to_major_map:
		minor = args.key
		major = minor_to_major_map[minor]
	else:
		major = args.key
		minor = None
	
	# check notes of each instrument (if applicable) to catch any out-of-normal-range notes
	converter = MMP_MusicXML_Converter(key_signature=major,
		params =
		{
		  'opts': args,
		  'minor': minor,
		})
	
	converter.convert_file(args.filename)
