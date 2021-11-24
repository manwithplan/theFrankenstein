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

    # initiliazing theVision module to get screenshots from the game window.
    visionMain = visionMain()
    visionMain.main()

    # initializing the detection module
    detector = detectionMain()

    # initializing the music module
    music = musicMain()
    music.openMusicPlayer()
    music.openStream()

    currentState = "Init"

    while True:

        if visionMain.screenFound:

            screenshots = visionMain.q.get()
            detector.runDetection(screenshots)

            print(detector.gameStateAvg)

            if currentState != detector.gameStateAvg:
                print("changed")
                newMusic = music.main(detector.gameStateAvg)
                if newMusic:
                    currentState = detector.gameStateAvg

        if keyboard.is_pressed("q"):
            print("q")
            visionMain.stopThread()
            music.closeMusicPlayer()
            break

    """
    app = QApplication(sys.argv)
    main = guiMain()
    main.setExternalFunctions(detectGameWindow)
    main.openLogin()
    sys.exit(app.exec_())
    """
