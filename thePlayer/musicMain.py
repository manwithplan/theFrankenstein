from typing import List, Set, Dict, Tuple, Optional, Union, Any, TypeVar
import logging
from fileinput import filename
import keyboard
import time
import numpy as np
import ast
import os
import traceback

from thePlayer.playerStream import playerStream
from thePlayer.databaseMain import databaseMain
from theUI.basicUI import getInput


class musicMain:
    """
    musicMain builds the logic that selects the music to be played.
    This module will take in commands from the user and select and write music to a queue.

    ...

    Attributes
    ----------
    player : obj
        playerStream object

    data : obj
        databaseMain object

    Methods
    -------
    main():
        Coördinates all music playback and database lookups.

    manualMode():
        Method used for testing functionality of music matching with user input rather that game input.

    openMusicPlayer():
        Sends an openStream command to the player object

    closeMusicPlayer():
        Sends a closeStream command to the player object

    Example commands :
    -------
    Write snippets to pipeline:
        self.piece = "Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3"
        self.snippetFileNames = []

        for x in range(1,49):
                self.snippetFileNames.append( self.piece + "_" + str(x) + ".wav")

        self.piece2 = "Concerto Grosso no. 4, HWV 322- I. Larghetto affettuoso.flac"
        self.snippetFileNames2 = []

        for x in range(1,22):
                self.snippetFileNames2.append( self.piece2 + "_" + str(x) + ".wav")

    Fade and mix into a new list of filenames:
        self.player.fadeAndMix( self.snippetFileNames2, location = 0 )

    Fade and stop playback:
        self.player.fadeAndStopPlayback()

    Write new snippets to pipeline:
        self.player.writeToPipeline( self.snippetFileNames )

    """

    def __init__(self) -> None:
        super().__init__()
        # initalize logger object
        self.logger: object = logging.getLogger(__name__)
        self.logger.info("music main initialized")

        # flag is True when playback is actvie
        self.playbackActive: bool = False

        # Create new custom pyaudio object, and open the stream.
        self.player: object = playerStream()

        # create object of databaseclass.
        self.data: object = databaseMain()

        # initiate a dict that links moods to gamestates. They mood keywords
        # will be ordered from most important to least important.
        self.moodToStateTranslator: Dict[str, List[str]] = {
            "conflictZone": ["epic", "dark", "scary"],
            "conflictDogFight": ["dark", "epic", "scary"],
            "planetaryLanding": ["epic", "romantic"],
            "docking": ["chilled", "calm", ""],
            "travel": ["romantic", "sad"],
            "canyonRunning": ["energetic", "epic"],
            "planetaryExploration": ["dark"],
            "slowTravel": ["sad", "chilled"],
            "None": [],
            "False": [],
        }

    def main(self, gameState: str) -> Union[None, TypeVar("pd.Series")]:
        """
        main method that coordinates all music playback and database lookups. It takes the game
        state and selects new music based on mood tags. This method is only called when a music
        switching event is called from the main method.

        :gameState: A string variable that represents the player's current action.
        :return: None if no matches have been found, else the matched row from the database
        """

        self.logger.info(f"main method called - gamestate: {gameState}")

        matchFound: bool = False

        # An attempt to find a match is made, if not, we will be returning None, and that will
        # be the flag to call the search method once more untill a match has been found.
        if not matchFound:
            try:
                mood: str = gameState

                if self.player.is_silent:
                    # In this case the player is not playing while we are looking for a match.
                    # The starting point for the music takes a random piece that coheres highly
                    # to the mood we are looking for and plays it from the start.

                    matches: TypeVar("pd.DataFrame") = self.data.findPieceByMood(mood)

                    if matches.empty:
                        raise KeyError

                    # choose one sample at random
                    match: TypeVar("pd.DataFrame") = matches.sample()
                    matchedRow: TypeVar("pd.Series") = matches.loc[
                        match.index.values[0]
                    ]

                    secondaryKey: str = str(int(matchedRow.PrimaryKeys)) + "_0000"
                    matchedRow: TypeVar("pd.Series") = self.data.df_snippets.loc[
                        self.data.df_snippets.SecondaryKeys == secondaryKey
                    ]

                    if matchedRow.empty:
                        raise KeyError

                    filenames: TypeVar("pd.Series") = self.data.gatherSnippets(
                        matchedRow
                    )
                    self.player.writeToPipeline(filenames)

                    matchFound: bool = True

                    # perform logging operations
                    self.logger.debug(f"player silent: {self.player.is_silent}")
                    self.logger.debug(f"matches found: {filenames}")

                    return matchedRow["PrimaryKeys"]

                else:

                    # from the pipeline of music currently played, get a snippet in the future.
                    # in this case 2 snippets from the current one being played.
                    toMatch: str = self.player.getFutureSnippet(2)

                    matches: TypeVar("pd.DataFrame") = self.data.findSimilarPiece(
                        toMatch, mood
                    )

                    if matches.empty:
                        raise KeyError

                    match: TypeVar("pd.DataFrame") = matches.sample()
                    matchedRow: TypeVar("pd.Series") = matches.loc[
                        match.index.values[0]
                    ]

                    filenames = self.data.gatherSnippets(matchedRow)
                    self.player.fadeAndMix(filenames, 0)

                    matchFound: bool = True

                    # perform logging operations
                    self.logger.debug(f"player silent: {self.player.is_silent}")
                    self.logger.debug(f"matches found: {filenames}")

                    return matchedRow["PrimaryKeys"]

            except IndexError as e:
                # perform logging operations
                self.logger.debug(f"matches found: None")
                return None

    def manualMode(self) -> None:
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

    def openStream(self) -> None:
        """
        Open stream by writing the first snippets to the snippet filenames.
        """
        self.logger.info(f"openStream method called")
        self.player.writeToPipeline(self.snippetFileNames)

    def openMusicPlayer(self) -> None:
        """
        Sends an openStream command to the player object
        """
        self.logger.info(f"openMusicPlayer method called")
        self.player.openStream()

    def closeMusicPlayer(self) -> None:
        """
        Sends a closeStream command to the player object
        """
        self.logger.info(f"openMusicPlayer method called")
        self.player.closeStream()
