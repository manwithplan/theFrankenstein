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
from theConductor.contextMain import contextMain

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
    # music.openStream()

    # initializing the context module
    context = contextMain()

    currentState = "False"

    while True:

        if visionMain.screenFound:

            screenshots = visionMain.q.get()
            detector.runDetection(screenshots)

            print(detector.gameStateAvg, end="\r")
            if not isinstance(detector.preview, type(None)):
                try:
                    cv2.imshow("test", detector.preview)
                    cv2.waitKey(1)
                except:
                    pass

            """

            new_context = context.main(currentState, detector.gameStateAvg)

            if new_context is False:
                currentState = detector.gameStateAvg

            elif not isinstance(new_context, type(None)):

                newMusic = music.main(new_context)
                print(newMusic, end="\r")
                if not isinstance(newMusic, type(None)):
                    currentState = detector.gameStateAvg

            print(f" music : {newMusic} - gamestate : {currentState}", end="\r")

            """

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
