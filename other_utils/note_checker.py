"""
many thanks to https://www.vsl.info/en/academy/index for providing instrument range info
(and a lot of other good info as well)

"""
import logging

class NoteChecker:

    # using # instad of b to match the note options in converter.py
    instrument_ranges = {
        "clarinet": {"min": "E3", "max": "C7"}, # E3-C7 is the valid range for clarinet
        "english horn": {"min": "E3", "max": "A5"},
        "oboe": {"min": "A#2", "max": "G6"}, #min listed as Bb3
        "bassoon": {"min": "A#0", "max": "D#4"}, #min listed as Bb1, max as Eb5
        "trombone": {"min": "E2", "max": "F5"},
        "horn": {"min": "B1", "max": "F5"},
        "tuba": {"min": "D1", "max": "G4"},
    }

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        
    def char_position(self, note: str):
        # assuming input looks like A1 or G5 or A#2
        return ord(note[0]) - 97
        
    def is_sharp(self, note: str):
        return '#' in note
        
    def extract_note_and_octave(self, note: str):
        if len(note) == 2:
            return note[0], int(note[1])
            
        if len(note) == 3:
            return note[:2], int(note[-1:])
            
        return None, None
    
    # test case: min is A#2 and note is A#1. A#1 should be invalid
    # test case: min is A#4, note is A4. A4 should be invalid
    def evaluate_note(self, instrument_name: str, note: str, octave: int, location=""):
        if instrument_name not in self.instrument_ranges:
            #TODO: maybe log a warning that this instrument doesn't exist?
            return
            
        valid_note = True
            
        min_note, min_octave = self.extract_note_and_octave(self.instrument_ranges[instrument_name]["min"])
        max_note, max_octave = self.extract_note_and_octave(self.instrument_ranges[instrument_name]["max"])
        print(f"min note: {min_note}, min octave: {min_octave}, max note: {max_note}, max octave: {max_octave}")
        
        # check if note octave falls in the octave range first
        if octave < min_octave or octave > max_octave:
            valid_note = False
        
        # if octaves are the same, then check the note (e.g. A1 should be considered invalid if the range min is D1)
        if octave == min_octave and self.char_position(note) < self.char_position(min_note):
            # e.g. if min is D3 and note is A3
            valid_note = False
            
        if octave == max_octave and self.char_position(note) > self.char_position(max_note):
            # e.g. if max is D3 and note is F3
            valid_note = False

        # special case for sharp min note
        if self.is_sharp(min_note):
            if not self.is_sharp(note) and self.char_position(note) == self.char_position(min_note):
                # if note is like A1 but min note is A#1
                valid_note = False
                
        if not valid_note:
            logging.debug(f"Warning: {note}{octave} is not within the expected range for {instrument_name}. @measure {location}")
            return False
            
        return valid_note
        
