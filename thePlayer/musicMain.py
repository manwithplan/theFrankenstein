"""

Module for building the logic that selects the music to be played.
This module will take in the gameState and other relevant information and write music to a queue

For the moment however I am still just debugging the stream player, and will simply hardcode it.

"""
import keyboard
from queue import Queue

from thePlayer.playerStream import playerStream

class musicMain():

        def __init__(self):
                super().__init__()

                self.playbackActive = False

                self.player = playerStream()

                self.piece = "Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3"
                self.snippetFileNames = []

                for x in range(1,49):
                        self.snippetFileNames.append( self.piece + "_" + str(x) + ".wav")

                self.piece2 = "Concerto Grosso no. 4, HWV 322- I. Larghetto affettuoso.flac"
                self.snippetFileNames2 = []

                for x in range(1,22):
                        self.snippetFileNames2.append( self.piece2 + "_" + str(x) + ".wav")

                

        def main(self, gameState):

                print('musicMain - {} detected - counter : {}'.format(gameState, self.player.pipelineCounter))

                if gameState == 'docking':

                        if not self.playbackActive:
                                self.playbackActive = True
                                self.player.writeToPipeline( self.snippetFileNames )

                elif gameState != "docking":

                        if self.playbackActive:
                                self.playbackActive = False
                                self.player.fadeAndStopPlayback()

        def test(self):

                print("\r counter = {}".format(self.player.pipelineCounter), end="")

                if keyboard.is_pressed('p'):

                        if not self.playbackActive:
                                self.playbackActive = True
                                self.player.writeToPipeline( self.snippetFileNames )

                elif keyboard.is_pressed('s'):

                        if self.playbackActive:
                                self.playbackActive = False
                                self.player.fadeAndStopPlayback()

                elif keyboard.is_pressed('m'):

                        if self.playbackActive:
                                self.player.fadeAndMix( self.snippetFileNames2, location = 0 )


        def openMusicPlayer(self):
                
                self.player.openStream()
                
        def closeMusicPlayer(self):

                self.player.closeStream()



