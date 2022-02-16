import threading
import time
from typing import List, Set, Dict, Tuple, Optional, Union, Any, TypeVar, Bytes
import logging
from PIL import Image
import numpy as np
import cv2
from queue import Queue

from Settings.Settings import shutterSpeed
from theVision.screenDetection import screenDetection
from theVision.imageConversion import imageConversion


class visionMain:
    """
    VisionMain combines all Computer Vision functions in this module and
    is responsible for finding the game window, extracting screenshots,
    processing and filtering them and applying all the detection algorhithms
    on them.

    ...

    Attributes
    ----------
    screenFound : bool
        Flag for the detection status of the game window

    boundingBox : List of ints
        List containing the coordinate of the game window.

    q : Queue
        The place where we store the images for processing.

    detectionRunning : bool
        Flag for the detection of the curren status.

    Methods
    -------

    thread() :
        returns the current image

    takeScreenshot() :
        Takes a screenshot of the window recognized as the game window.

    main() :
        main function that starts the threads.

    stopThread():
        Function that stops the threads.

    """

    def __init__(self, screenName=None):
        super().__init__()
        self.logger: object = logging.getLogger(__name__)
        self.logger.info("visionMain object initialized")

        # global variables
        self.screenFound = False

        # bounding box for storing the window coordinates.
        self.boundingBox = []

        # set-up the queue
        self.q = Queue()

        # threading variables
        self.threads = []
        self.t = None

        # detection variables
        if not screenName:
            self.detector = screenDetection()
        else:
            self.detector = screenDetection(screenName=screenName)
        self.detectionRunning = True
        self.screenCoordinates = None

        # imageConversion variables
        self.converter = imageConversion()

    def thread(self, mode: int = 1) -> None:
        """
        Method that takes the screenshot of the game window and processes it to the correct
        format and color filters for detection.

        :mode: diversifies the filtering process between 2 options, either running a neural network (0)or running object detection(1).
        """

        self.logger.info(f"detection started - mode : {mode}")

        while self.detectionRunning:
            # sleep on each cycle. Duration determined in settings.
            time.sleep(shutterSpeed)

            # screenShotting mode
            if self.detector.screenOpen:

                # if no coordinates are known, we'll try to get them again.
                if self.screenCoordinates is not None:
                    img = self.takeScreenshot()

                    self.converter.loadScreenshotImage(img)

                    if mode == 0:
                        self.converter.resizeImage()
                        result = self.converter.applyAllFiltersToRGB()
                        # result = self.converter.getImageAsPIL(result)
                    else:
                        # returning a filtered image as a result. Currently this only filters for HUD detection
                        # but this will expand for different objects.
                        resultWhite = self.converter.filterImage(
                            "white", self.converter.image
                        )
                        resultGray = self.converter.filterImage(
                            "supercruise", self.converter.image
                        )
                        resultHUD = self.converter.filterImage(
                            "hud", self.converter.image
                        )
                        resultDocking = self.converter.filterImage(
                            "docking", self.converter.image
                        )
                        resultConflict = self.converter.filterImageRed(
                            self.converter.filtersRed["lowRed"],
                            self.converter.filtersRed["highRed"],
                            self.converter.image,
                        )

                    self.screenFound = True

                    self.q.put(
                        [
                            resultHUD,
                            resultDocking,
                            resultConflict,
                            resultWhite,
                            resultGray,
                        ]
                    )

                else:
                    print("screen found, loading coördinates")
                    self.screenCoordinates = self.detector.getScreenCoordinates()

                    # there is a difference between the way the coördinates are ordered in the 2 libraries communicating here,
                    # that is PIL(top, left, width, height) and win32gui (left, top, right, bottom). That means that I need to
                    # calculate width and height from the given coordinates as so:

                    self.boundingBox["left"] = self.screenCoordinates[0] + 11
                    self.boundingBox["top"] = self.screenCoordinates[1] + 31
                    self.boundingBox["width"] = (
                        self.screenCoordinates[2] - self.screenCoordinates[0] - 22
                    )
                    self.boundingBox["height"] = (
                        self.screenCoordinates[3] - self.screenCoordinates[1] - 42
                    )

                    self.logger.debug(
                        f"screen found with coördinates - {self.boundingBox}"
                    )

            # detection mode
            else:
                self.detector.checkGameActive()
                self.screenFound = False
                self.logger.debug(f"screen not found")

    def takeScreenshot(self) -> TypeVar("np.array"):
        """
        Takes a screenshot of the window video using the coordinates stored in the
        bounding box variabel.

        :return: a numpy array representation of the game window.
        """
        self.logger.debug(f"screenshot taken of window {self.boundingBox}")
        return np.array(self.sct.grab(self.boundingBox))

    def main(self) -> None:
        """
        main function that starts the threads.
        """
        self.t = threading.Thread(target=self.thread)
        self.threads.append(self.t)
        self.t.start()
        self.logger.info(f"visonMain thread started")

    def stopThread(self) -> None:
        """
        Function that stops the threads.
        """
        print("stopped")
        self.detectionRunning = False
        self.t.join()
        self.logger.info(f"visonMain thread stopped")
