## 🎶 .mmp to MusicXML 🎶    
A Python module that attempts to convert .mmp files (which are XML files :D) to MusicXML files so that you can import them to MuseScore!    
    
The idea is to help provide significant time savings in getting your music from LMMS to sheets. :)    
    
### USAGE:    
You can just run `python convert-mmp.py [file path to an .mmp file]` or import the module into another script and use it there.    
    
The output will be named whatever the file's name is as an xml file in the same directory. You can then use MuseScore to view it. I've not tested with other notation software.    
    
some things to note as of now:    
- the smallest note type the script can understand is a 64th note, so anything smaller will break things 
- no tied and/or dotted notes
- can't identify intended triplets
- notes that extend past a measure are truncated to fit in the measure they start in
- I've specified some instruments for the program to identify based on the track names - i.e. flute, piano, clarinet since I work with a lot of those instrument soundfonts. I should extend this to accept TripleOscillator tracks, for example, though as well.    
- Additionally, I've added a rudimentary note checking feature that'll evaluate certain instruments' notes (see `mmp_to_musicxml/utils/note_checker.py`) and output warnings for any notes that don't fall in the traditional range.    
    
You can try out the script with the included test .mmp files, or check out some of my results in `/example_output`!    
    
For testing, I used pytest, which you can install via `pip install pytest`. You can run the tests just by entering `pytest` while in the project directory.    
    
I also have some documentation made with Sphinx in docs/build/html.    
    
Turn this:    
![lmms .mmp project](images/lmms.png)    
    
which is actually something like this:    
![lmms .mmp project in xml](images/mmp.png)    
    
into this:    
![musicxml file from .mmp into MuseScore](images/musescore.png)    

