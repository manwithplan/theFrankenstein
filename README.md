# The FrankenStein

## Table of Contents
1. [Description](#description)
	1. [Repo Architecture](#repo-architecture)
	2. [Modules](#Modules)
2. [Installation](#installation)
3. [Tech](#tech)

# Description

A music player that mixes existing pieces of music together to form an interactive score generated on the fly.

## Repo Architecture
```
Project/
|-- Settings/
|   |-- loggins.conf
|   |-- Settings.py
|-- theConductor/
|   |-- contextMain.py
|-- theDB/
|-- theGUI/
|   |-- resources/
|   |-- ui/
|   |-- main.py
|-- theMusic/
|-- thePlayer/
|   |-- databaseMain.py
|   |-- musicMain.py
|   |-- playerStream.py
|-- theResources/
|-- theTools/
|   |-- debugMain.py
|   |-- imageGrab.py
|   |-- objectDetection.py
|-- theUI/
|   |-- basicUI.py
|-- theVision/
|   |-- detectionMain.py
|   |-- imageConversion.py
|   |-- screenDetection.py
|   |-- visionMain.py
|-- README.md
|-- .gitignore
|-- app.py
```

## Modules

### The Mixer

The mixer takes a piece in and looks through a database with relevant musical information on :
- harmonic context
- rhythmic context
- mood analysis 
- and other datapoints, like valence, arousal, signal quality and instrumentation
and finds a close match to transition into in less than a tenth of a second.

### The Player

Custom built PyAudio class that creates an audio stream playing back sound fragments and mixes them together
as seamless as possible.

It creates a silent stream when opened, that has the correct frame rate, format and channels, and using 
PyAudio's inbuilt callback methods reads data from a pipeline.

There are functions that control the mixing using fade-ins and fade-outs.

### The Features

All music is splitted down to segments as long as a bar, and on each of these a seperate analysis is performed. 
This allows very localized information to be gathered and a very accurate similarity to be caculated.

These features include, but are not limited to harmonic context like what notes are played, what chord is 
played and what key the segment is in. Rhythmic context featureing beat onsets and tempo measurements local and
local. MIR features like Valence and Arousal. And metadata like composer, instrumentation and audio Quality.

### The Moods

All music has been analyzed beforehand by mood keywords, and these are used as entrypoints into the game that
is being scored to. In this case Elite: Dangerous. If there is a tense scene it will look for 'dark' or
'epic' music. If not much is happening, it will be 'calm' or 'peaceful' music.

A matrix is defined that defines in what way the music should change when going from one game state to another.

### The Changes

The matrix looks like this had in the x-axis the previous game state and on the y-axis the next game-state and 
the content in the each looked-up cell holds information that controls the music by altering the similarity and
mood searches.

The matrix also takes into account the results of 2 more subsystems:
1 : a location awareness system (time since player in gamestate, location in gaming session)
2 : a context awareness system (mood matching current gamestate, musical activity recquired for that state) 

### The State

The gamestate is extracted in theVision module, where the game screen is located, analyzed and a detection
is made based an the combination of several different detection algorhithms combined.

## Installation
- Running this app requires a running version of **Elite: Dangerous**
- Clone the repository and install the dependencies with `requirements.txt`
- Run `app.py` to execute the script.

## Tech
The source code uses the folowing libraries:

- **Pillow**, **OpenCV** and **MatPlotLib** for computer vision
- **PyAudio** and **PyDub** for audio signal processing
- **Pandas** for data processing
- **PySide6** for the GUI
- **Numpy** for fun
- 
**[Back to top](#table-of-contents)**
