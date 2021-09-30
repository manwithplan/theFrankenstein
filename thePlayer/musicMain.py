import keyboard
import time

from thePlayer.playerStream import playerStream
from thePlayer.databaseMain import databaseMain

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

                self.piece = "Goldberg Variations, BWV 988 - 01 - Aria.mp3"
                self.snippetFileNames = []

                for x in range(1,49):
                        self.snippetFileNames.append( self.piece + "_" + str(x) + ".wav")

        def main(self):
                print('loop has been opened')
                self.player.openStream()
                print('stream opened', end = "\r")

                while True:
                        time.sleep(1)
                        try:
                                toMatch = self.player.getFutureSnippet(2)
                                matches = self.data.findSimilarPiece(toMatch)
                        except:
                                pass

                        if keyboard.is_pressed('s'):
                                # write a list of snippet filenames to the stream, playback begins immediatly
                                self.player.writeToPipeline( self.snippetFileNames )
                                print('files written', end = "\r")

                        elif keyboard.is_pressed('n'):
                                print('mixin initialized', end = "\r")
                                # Fading between 2 similar peices of music. First get the snippet we will be working on
                                #toMatch = self.player.getFutureSnippet(2)
                                # then find a piece of music that is similar to the one playing now.
                                #filenames = self.data.findSimilarPiece(toMatch)
                                # initiate the fade.
                                filenames = self.data.gatherSnippets(matches.iloc[[1]])
                                self.player.fadeAndMix(filenames, 0)
                                print('mixing complete', end = "\r")

                        elif keyboard.is_pressed('q'):
                                # close stream and stop playback
                                self.player.fadeAndStopPlayback()
                                self.player.closeStream()
                                print('stream closing', end = "\r")
                                break

        def openMusicPlayer(self):
                
                self.player.openStream()
                
        def closeMusicPlayer(self):

                self.player.closeStream()



