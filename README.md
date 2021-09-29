# The FrankenStein

Based on an old project, I have a dataset of 800+ pieces of classical music 
divided into snippets by **beat**.

I have analyzed the music for each snippet seperately using libraries like
*madmom*, which is built by the AI division of the University of Vienna.
It can be freely imported into any Python script.

### The Mixer

The feature I will be building this week is a real-time mixer. It should be 
capable of:

1. taking in a reference snippet of music, look through the various
databases of Music Informatics and find the closest match based on those
values.

2. play the result in sequence with the piece of music currently playing
and continue playback from that point in the matched piece of music.

3. Mix the 2 snippets together in a smooth way.