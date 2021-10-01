import keyboard
import time
import numpy as np
import ast
import os

from thePlayer.playerStream import playerStream
from thePlayer.databaseMain import databaseMain
from theUI.basicUI import getInput

class musicMain():

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

                self.playbackActive = False
                self.player = playerStream()
                self.data = databaseMain()

                self.piece = "Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3"
                self.snippetFileNames = []

                for x in range(1,49):
                        self.snippetFileNames.append( self.piece + "_" + str(x) + ".wav")

        def main(self):
                os.system('cls')
                print('loop has been opened')
                self.player.openStream()
                print('stream opened', end = "\r")
                self.UI = getInput() 


                while True:
                        
                        time.sleep(3)
                        

                        try:
                                toMatch = self.player.getFutureSnippet(2)
                                matches = self.data.findSimilarPiece(toMatch)

                                # getting the moods from an unordered csv is about as bad as solving regex exercises.
                                allMoods = matches['Moods'].tolist()
                                allMoods = [item for sublist in allMoods for item in sublist]
                                allMoods = str(allMoods).replace(",", "','").replace("' '", "'").replace("''", "'").replace(" ", "")
                                allMoods = list(set(ast.literal_eval(allMoods)))

                                os.system('cls')
                                print("mix : random", end = "\n")
                                for idx, x in enumerate(allMoods):
                                        print(f"{idx} : {x}", end = "\n")
                                                               
                        except Exception as e:
                                pass


                        try:
                                if self.UI.userInput == "start":
                                        # write a list of snippet filenames to the stream, playback begins immediatly
                                        self.player.writeToPipeline( self.snippetFileNames )
                                        print('files written')

                                elif self.UI.userInput.isnumeric():
                                        print('mixing initialized')

                                        # get the mood that we selected from the user input
                                        mood = allMoods[int(self.UI.userInput)]
                                        
                                        # from the matches that match our mood select a random one by index
                                        matchesIndex = matches.filter(like=mood, axis=1)
                                        match = matchesIndex.sample()
                                        
                                        matchedRow = matches.loc[match.index.values[0]]

                                        filenames = self.data.gatherSnippets(matchedRow)
                                        self.player.fadeAndMix(filenames, 0)
                                        print('mixing complete')

                                elif self.UI.userInput == "x":
                                        print('mixing initialized')
                                        print(allMoods[self.UI.userInput])
                                        filenames = self.data.gatherSnippets(matches.iloc[[1]])
                                        self.player.fadeAndMix(filenames, 0)
                                        print('mixing complete')

                                elif self.UI.userInput == "stop":
                                        # close stream and stop playback
                                        self.player.fadeAndStopPlayback()
                                        self.player.closeStream()

                                        # close the UI thread
                                        self.UI.stopFlag = True
                                        self.UI.join()
                                        print('stream closing')
                                        break
                        except:
                                pass

                        self.UI.clearInput()

        def openMusicPlayer(self):
                
                self.player.openStream()
                
        def closeMusicPlayer(self):

                self.player.closeStream()



