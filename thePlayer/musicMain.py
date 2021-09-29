import keyboard
from queue import Queue

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

                self.piece = "Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3"
                self.snippetFileNames = []

                for x in range(1,49):
                        self.snippetFileNames.append( self.piece + "_" + str(x) + ".wav")

        def main(self):

                while True:

                        if keyboard.is_pressed('o'):
                                self.player.openStream()
                        elif keyboard.is_pressed('s'):
                                self.player.writeToPipeline( self.snippetFileNames )
                        elif keyboard.is_pressed('n'):
                                toMatch = self.player.getFutureSnippet(2)
                                self.data.findSimilarPiece(toMatch)
                                self.player.fadeAndMix()
                        elif keyboard.is_pressed('q'):
                                self.player.closeStream()
                                break

        def openMusicPlayer(self):
                
                self.player.openStream()
                
        def closeMusicPlayer(self):

                self.player.closeStream()



