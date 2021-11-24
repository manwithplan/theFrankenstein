# import libraries
import sys
import time
import keyboard
from PySide6.QtWidgets import QApplication
from queue import Queue
import cv2

# import modules
from theVision.visionMain import visionMain
from theVision.detectionMain import detectionMain

from thePlayer.musicMain import musicMain

from theGUI.main import guiMain

if __name__ == "__main__":

    # initializing the music module
    music = musicMain()
    music.openMusicPlayer()
    music.openStream()

    music.main("conflictZone")

    time.sleep(2)

    music.closeMusicPlayer()
