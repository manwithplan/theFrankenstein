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

### The Moods

Currentlty I can find these moods most often: 
['sad', 'dark', 'energetic', 'epic', 'happy', 'chilled', 'scary', 'romantic', 'ambiguous', 'spherical', 'calm']

Now I have to link them to the actions in the game.
['conflictZone', 'conflictDogFight', 'planetaryLanding', 'docking', 'travel', 'canyonRunning', 'planetaryExploration', 'slowTravel', 'Menu', 'False']

conflictZone => epic, dark, energetic, scary
conflictDogFight => epic, energetic, scary
planetaryLanding => epic, romantic, spherical
docking => chilled, spherical, calm
travel => romantic, spherical, sad
canyonRunning => energetic, epic, happy
planetaryExploration => spherical, dark
slowTravel => chilled, sad

Besides linking the detections to moods, they should also be linked to a 'music 
level'. How much music is necessary to supplement or reinforce the current scene.
This can be just a float variable depicting the level of music and rules of 
selection and playback

Support should be there for selecting on the basis of multiple tags!

### TODO

- Use different starting points for music, or code some logic that selects a new starting point. (musicMain line 68)
- Use filter method to select by multiple possible moods. (musicMain line 91)