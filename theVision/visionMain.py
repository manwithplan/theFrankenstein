"""

main vision class : weaves together the imageConversion, imageGrab and screenDetection in this package using threading

1: thread function. Functionality to be run in thread. A decision tree that switches between detection and screenShotting

"""

# import libraries
import threading
import time
from PIL import Image
import numpy as np
import cv2
from queue import Queue

# import modules
from Settings.Settings import shutterSpeed
from theVision.screenDetection import screenDetection
from theVision.imageGrab import findScreen
from theVision.imageConversion import imageConversion

class visionMain():
    def __init__(self):
        super().__init__()
        # global variables
        self.screenFound = False

        # set-up the queue
        self.q = Queue()

        # threading variables
        self.threads = []
        self.t = None

        # detection variables
        self.detector = screenDetection()
        self.detectionRunning = True
        self.screenCoordinates = None

        # imageGrab variables
        self.grabber = findScreen()

        # imageConversion variables
        self.converter = imageConversion()

    def thread(self, mode = 1):
        # mode diversifies the filtering process between 2 options, either running a neural network (0)or running object detection(1).
        # attach a global running flag to the process
        print('detection started - mode : {}'.format(mode))
        
        while self.detectionRunning:
            # sleep on each cycle. Duration determined in settings.
            time.sleep( shutterSpeed )

            # screenShotting mode
            if self.detector.screenOpen:

                # if no coordinates are known, we'll try to get them again.
                if self.screenCoordinates is not None:
                    img = self.grabber.takeScreenshot()

                    self.converter.loadScreenshotImage(img)

                    if mode == 0:
                        self.converter.resizeImage()
                        result = self.converter.applyAllFiltersToRGB()
                        #result = self.converter.getImageAsPIL(result)
                    else:
                        # returning a filtered image as a result. Currently this only filters for HUD detection 
                        # but this will expand for different objects.
                        resultWhite = self.converter.filterImage('white', self.converter.image)
                        resultGray = self.converter.filterImage('supercruise', self.converter.image)
                        resultHUD = self.converter.filterImage('hud', self.converter.image)
                        resultDocking = self.converter.filterImage('docking', self.converter.image)
                        resultConflict = self.converter.filterImageRed( self.converter.filtersRed['lowRed'], self.converter.filtersRed['highRed'], self.converter.image)

                        
                    self.screenFound = True

                    self.q.put([resultHUD, resultDocking, resultConflict, resultWhite, resultGray])
                   
                    # In case you want to show the image for debugging:
                    """
                    numpy = np.array(result)
                    cv2.imshow('img', numpy)
                    cv2.waitKey(1)
                    """
                    
                else: 
                    print('screen found, loading coördinates')
                    self.screenCoordinates = self.detector.getScreenCoordinates()

                    # there is a difference between the way the coördinates are ordered in the 2 libraries communicating here, 
                    # that is PIL(top, left, width, height) and win32gui (left, top, right, bottom). That means that I need to 
                    # calculate width and height from the given coordinates as so:

                    self.grabber.boundingBox['left'] = self.screenCoordinates[0] + 11
                    self.grabber.boundingBox['top'] = self.screenCoordinates[1] + 31
                    self.grabber.boundingBox['width'] = self.screenCoordinates[2] - self.screenCoordinates[0] - 22
                    self.grabber.boundingBox['height'] = self.screenCoordinates[3] - self.screenCoordinates[1] - 42

            # detection mode
            else: 
                self.detector.checkGameActive()
                self.screenFound = False
                print('screen not found', end="\r" )

    def main(self):
        self.t = threading.Thread(target=self.thread)
        self.threads.append(self.t)
        self.t.start()

    def stopThread(self):
        print('stopped')
        self.detectionRunning = False
        self.t.join()

