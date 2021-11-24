import keyboard
import time
import numpy as np
import ast
import os

from thePlayer.playerStream import playerStream
from thePlayer.databaseMain import databaseMain
from theUI.basicUI import getInput


class musicMain:

    """

        Module for building the logic that selects the music to be played.
        This module will take in commands from the urser and select and write music to a queue.

        Example commands :

        self.piece = "Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3"
                self.snippetFileNames = []

                for x in range(1,49):
                        self.snippetFileNames.append( self.piece + "_" + str(x) + ".wav")

                self.piece2 = "Concerto Grosso no. 4, HWV 322- I. Larghetto affettuoso.flac"
                self.snippetFileNames2 = []

                for x in range(1,22):
                        self.snippetFileNames2.append( self.piece2 + "_" + str(x) + ".wav")

        self.player.fadeAndMix( self.snippetFileNames2, location = 0 )

        self.player.fadeAndStopPlayback()

        self.player.writeToPipeline( self.snippetFileNames )

        """

    def __init__(self):
        super().__init__()

        # flag is True when playback is actvie
        self.playbackActive = False

        # Create new custom pyaudio object, and open the stream.
        self.player = playerStream()

        # create object of databaseclass.
        self.data = databaseMain()

        # initiate a dict that links moods to gamestates. They mood keywords
        # will be ordered from most important to least important.
        self.moodToStateTranslator = {
            "conflictZone": ["epic", "energetic", "dark", "scary"],
            "conflictDogFight": ["dark", "epic", "scary"],
            "planetaryLanding": ["epic", "romantic", "spherical"],
            "docking": ["chilled", "calm", "spherical"],
            "travel": ["romantic", "spherical", "sad"],
            "canyonRunning": ["energetic", "epic", "happy"],
            "planetaryExploration": ["spherical", "dark"],
            "slowTravel": ["sad", "chilled"],
            "None": [],
            "False": [],
        }

        # Currently still using this piece as the starting point.
        self.piece = "Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3"
        self.snippetFileNames = []

        for x in range(1, 49):
            self.snippetFileNames.append(self.piece + "_" + str(x) + ".wav")

    def openStream(self):
        self.player.writeToPipeline(self.snippetFileNames)

    def main(self, gameState):
        """
        main method that coordinates all music playback and database lookups. It takes the game 
        state and selects new music based on mood tags. This method is only called when a music
        switching event is called from the main method.

        :gameState: A string variable that represents the player's current action. 
        :return: None if no matches have been found, else the matched row from the database
        """

        matchFound = False

        # An attempt to find a match is done 3 times, if not, we will be returning None, and that will
        # be the flag to call the search method once more untill a match has been found.
        if not matchFound:
            tries = 3
            for i in range(tries):
                try:
                    moods = self.moodToStateTranslator[gameState].copy()

                    # Take the first element in the possible moods, and look it up, then delete it from the list.
                    mood = moods[i]

                    # from the pipeline of music currently played, get a snippet in the future.
                    # in this case 2 snippets from the current one being played.
                    toMatch = self.player.getFutureSnippet(2)
                    matches = self.data.findSimilarPiece(toMatch)

                    # from the matches that match our mood select a random one by index
                    matchesIndex = matches.Moods.str.contains(mood)

                    # Check if a result has been found, else raise an error.
                    if matchesIndex.empty:
                        raise KeyError

                    match = matchesIndex.sample()
                    matchedRow = matches.loc[match.index.values[0]]

                    filenames = self.data.gatherSnippets(matchedRow)
                    self.player.fadeAndMix(filenames, 0)

                    matchFound = True
                    return matchedRow["PrimaryKeys"]

                except KeyError as e:
                    if i < tries - 1:  # i is zero indexed
                        print(e)
                        continue
                    else:
                        pass

                except IndexError as e:
                    print(e)
                    return None

                break

    def manualMode(self):
        """
        method used for testing functionality of music matching with user input rather that game input.
        """
        os.system("cls")
        print("loop has been opened")
        print("stream opened", end="\r")
        self.UI = getInput()

        while True:

            time.sleep(3)

            try:
                toMatch = self.player.getFutureSnippet(2)
                matches = self.data.findSimilarPiece(toMatch)

                # getting the moods from an unordered csv is about as bad as solving regex exercises.
                allMoods = matches["Moods"].tolist()
                allMoods = [item for sublist in allMoods for item in sublist]
                allMoods = (
                    str(allMoods)
                    .replace(",", "','")
                    .replace("' '", "'")
                    .replace("''", "'")
                    .replace(" ", "")
                )
                allMoods = list(set(ast.literal_eval(allMoods)))

                os.system("cls")
                print("mix : random", end="\n")
                for idx, x in enumerate(allMoods):
                    print(f"{idx} : {x}", end="\n")

            except Exception as e:
                pass

            try:
                if self.UI.userInput == "start":
                    # write a list of snippet filenames to the stream, playback begins immediatly
                    self.player.writeToPipeline(self.snippetFileNames)
                    print("files written")

                elif self.UI.userInput.isnumeric():
                    print("mixing initialized")

                    # get the mood that we selected from the user input
                    mood = allMoods[int(self.UI.userInput)]

                    # from the matches that match our mood select a random one by index
                    matchesIndex = matches.filter(like=mood, axis=1)
                    match = matchesIndex.sample()

                    matchedRow = matches.loc[match.index.values[0]]

                    filenames = self.data.gatherSnippets(matchedRow)
                    self.player.fadeAndMix(filenames, 0)
                    print("mixing complete")

                elif self.UI.userInput == "x":
                    print("mixing initialized")
                    print(allMoods[self.UI.userInput])
                    filenames = self.data.gatherSnippets(matches.iloc[[1]])
                    self.player.fadeAndMix(filenames, 0)
                    print("mixing complete")

                elif self.UI.userInput == "stop":
                    # close stream and stop playback
                    self.player.fadeAndStopPlayback()
                    self.player.closeStream()

                    # close the UI thread
                    self.UI.stopFlag = True
                    self.UI.join()
                    print("stream closing")
                    break
            except:
                pass

            self.UI.clearInput()

    def openMusicPlayer(self):

        self.player.openStream()

    def closeMusicPlayer(self):
        self.player.closeStream()

