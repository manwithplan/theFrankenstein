# The FrankenStein

A music player that mixes existing pieces of music together to form an interactive score to the real world.

### The Mixer

The mixer takes a piece in and looks through a database with relevant musical information on :
- harmonic context
- rhythmic context
- mood analysis 
- other datapoints, like valence, arousal, signal quality and instrumentation
and finds a close match to mix into in less than a tenth of a second.

### The Player

Custom built PyAudio class that creates an audio stream playing back sound fragments and mixing them together
as close to seamlessly as possible.

### The Moods

All music has been analyzed beforehand by mood keywords, and these as entrypoints into the game dat is being scored to.
In this case Elite: Dangerous.

A matrix is defined that defines in what way the music should change when going from one game state to another.

### The Changes

The matrix looks like this:

xx  CZ  CD  PL  DO  TR  CR  PE  ST  
CZ  
CD  
PL  
DO  
TR  
CR  
PE  
ST  

x-axis : current game-state
y-axis : new game-state

Beyond this 2 more tools have been built:
1 : a location awareness system (time since player in gamestate, location in gaming session)
2 : a context awareness system (mood matching current gamestate, musical activity recquired for that state) 

### varia

Currentlty I can find these moods most often: 
['Dark','Chill','Epic','Scary','Ethereal','Calm','Sad','Romantic']

Now I have to link them to the actions in the game.
['conflictZone', 'conflictDogFight', 'planetaryLanding', 'docking', 'travel', 'canyonRunning', 'planetaryExploration', 'slowTravel', 'Menu', 'False']

conflictZone => epic, dark, scary
conflictDogFight => epic, scary
planetaryLanding => epic, romantic
docking => chilled, calm
travel => romantic, sad
canyonRunning => epic
planetaryExploration => dark, scary, calm
slowTravel => chilled, sad

