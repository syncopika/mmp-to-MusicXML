## .mmp to MusicXML 🎶 👏    
Currently a basic script that attempts to convert .mmp files (which are XML files) to MusicXML files so that you can import them to MuseScore!    
Still potentially buggy, but the idea is to help provide significant time savings in getting your music from LMMS to sheets. :)    
    
usage (I'm using Python 3.5 btw):    
`python mmp-to-musicXML.py [file path]`    
    
The output will be named whatever the file's name is as an xml file. You can then use MuseScore to view it.    
    
some things to note as of now:    
- the smallest note type the script can understand is a 64th note, so anything smaller will break things 
- no tied and/or dotted notes
- can't identify intended triplets
- I've specified some instruments for the program to identify based on the track names - i.e. flute, piano, clarinet since I work with a lot of those instrument soundfonts. I should extend this to accept TripleOscillator tracks, for example, though as well.    
    
You can try out the script with the included test .mmp files, or check out some of my results in /example_output!    
    
Turn this:    
![lmms .mmp project](images/lmms.png)    
    
into this:    
![musicxml file from .mmp into MuseScore](images/musescore.png)    

