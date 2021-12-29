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

TODO!!! You REALLY need the localized version of the music moods, because currently it is simply 
inaccurate. That would go a very long way in getting the app to run!

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

### The Changes

There should be logic that controls when the switch actually occurs.

1 : When the music starts is actually quite important. It can't just start when the game starts.
It should actually be slightly randomized but also adaptive to the current scene we're scoring to.

2 : You don't just want music to be played the whole time, somehow you need to wait at certain times. 

How do you capture these features in a logic that we can maintain throughout playback?

I'm going to use a self-similarity matrix, with gamestates on the x axis, and on the y-axis
you can say that the current state is on the x -axis and the new state is on the y-axis customizing each
possible sequence of events.

xx  CZ  CD  PL  DO  TR  CR  PE  ST  
CZ  
CD  
PL  
DO  
TR  
CR  
PE  
ST  

Music should be defined by these factors:
- The mood that matches the current gamestate
- The time since playback began. The music should have pauses in it: moments where less musical activity 
takes place.
- This should be controlled by a musical activity level.
- The time since which a new gamestate has been set.

You can break these up in 2 categories:
1 : location awareness system(time since player in gamestate, location in gaming session)
2 : Context awareness system(mood matching current gamestate, musical activity recquired for that state) 

### TODO

- Use different starting points for music, or code some logic that selects a new starting point. (musicMain line 68)
- Use filter method to select by multiple possible moods. (musicMain line 91)