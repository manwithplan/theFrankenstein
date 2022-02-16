import numpy as np
import cv2
from mss import mss
from PIL import Image
import keyboard
import time


class findScreen:

    """
    This class is Not used in the project. It is here for looking up purposes.

    It is designed to automatically find a video image anywhere on the sreen.

    the imageGrab module is used to grab images from the screen, to be formatted and
    sent through the neural network for a prediction. findScreen class is used for
    testing, as it finds a video window that hasn't been set before. In production
    we will know the name of the window from which to take a screenShot, and that
    will be a different class.

    ...

    Attributes
    ----------
    image : PIL Image
        The image being processed

    filters : List of str
        List containing threshold values for HSV filtering of incoming images

    filtersDed : List of str
        List containing threshold values for HSV filtering of incoming images for the color red

    Methods
    -------

    """

    # My script now accurately tells where the moving images are, I can go from here on out and match templates to the different GUI elements, and reading the map.
    # Once I have done this, I can quantify that data into a sentiment compas and use that to trigger tracks.

    def __init__(self):
        super().__init__()

        self.boundingBox = {"top": 100, "left": 960, "width": 960, "height": 1080}

        # average coördinates
        self.videoCoordinates = {
            "x": list(range(1, 10)),
            "y": list(range(1, 10)),
            "w": list(range(1, 10)),
            "h": list(range(1, 10)),
        }

        # optimal coordinates (coordinates per axis, accuracy level)
        self.optimalCoordinates = {"x": [], "y": [], "w": [], "h": []}

        self.sct = mss()

    # mathematical functions in support of others defined here

    def mostFrequent(self, theList):
        mostOccured = max(set(theList), key=theList.count)
        accuracy = theList.count(mostOccured) / len(theList)

        return [mostOccured, accuracy * 100]

    # computer vision functions defined below

    def rectangleDrawer(self, img, x1, y1, x2, y2):
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
        return img

    def trackWindow(self, avg):

        # the function below attempts to find the game window that is being used as accurately as possible.
        # We can still optimize the speed at which it is found by limiting the length of self.videoCoordinates stored,
        # by not only appending, but also popping.

        # making a copy of the weighted average, to draw shapes on.
        avgDrawn = avg.copy()

        # convert the average into a usable filtype for thresholding
        frameGray = avgDrawn.astype(np.uint8)
        frameGray = cv2.cvtColor(frameGray, cv2.COLOR_BGR2GRAY)

        # you need this for the erosion and dilation
        kernel = np.ones((5, 5), np.uint8)

        # The first parameter is the original image, kernel is the matrix with which image is convolved and third parameter is the number
        # of iterations, which will determine how much you want to erode/dilate a given image.
        frameGray = cv2.erode(frameGray, kernel, iterations=5)
        frameGray = cv2.dilate(frameGray, kernel, iterations=5)

        # finding contours
        ret, thresh = cv2.threshold(frameGray, 0, 255, 0)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            c = max(contours, key=cv2.contourArea)

            x, y, w, h = cv2.boundingRect(c)

            # the next steps are looking to optimize the rectangle that has been drawn. The way they do that is by storing all the
            # found coordinates in the last step, every n frames. And subsequently counting the most occuring element in it.
            # By dividing this by the total number of found coördinates it gives you an accuracy %. Once a certain leverl of accuracy is µ
            # found we should have the best approximation of our video screen.
            # storing all the coördinates in order to optimize where the video screen is.
            self.videoCoordinates["x"].append(x)
            self.videoCoordinates["x"].pop(0)
            self.videoCoordinates["y"].append(y)
            self.videoCoordinates["y"].pop(0)
            self.videoCoordinates["w"].append(w)
            self.videoCoordinates["w"].pop(0)
            self.videoCoordinates["h"].append(h)
            self.videoCoordinates["h"].pop(0)

            self.optimalCoordinates["x"] = self.mostFrequent(self.videoCoordinates["x"])
            self.optimalCoordinates["y"] = self.mostFrequent(self.videoCoordinates["y"])
            self.optimalCoordinates["w"] = self.mostFrequent(self.videoCoordinates["w"])
            self.optimalCoordinates["h"] = self.mostFrequent(self.videoCoordinates["h"])

            accuracyCoordinates = (
                self.optimalCoordinates["x"][1]
                + self.optimalCoordinates["y"][1]
                + self.optimalCoordinates["w"][1]
                + self.optimalCoordinates["h"][1]
            ) / 4

            # draw the biggest contour (c) in green
            cv2.rectangle(avgDrawn, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # cv2.drawContours(avgDrawn, contours, -1, (0,255,0), 10)

        return avgDrawn, accuracyCoordinates

    # executive function called here, these are basically the functions that sequence and call the opencv functions.

    def callTracker(self, frame, originalBox, avg):

        # counting all the frames that pass allows me to schedule certain functions in sequence.
        frameCount = 0

        # the next boolean represents whether we found the game window with reasonable accuracy
        windowFound = False

        while True:

            # the next line grabs the frames from the bounding box area we defined earlier
            frame2 = frame
            frame1 = self.sct.grab(originalBox)

            # computes the difference between two frames, in order to get an apporximation of the moving area, in this case hopefully the game screen.
            diff = cv2.absdiff(np.float32(frame1), np.float32(frame2))

            # computes a running average of the moving parts
            cv2.accumulateWeighted(diff, avg, 0.3)

            # below I can schedule the callback of functions based on the amount of frameCounts.

            if frameCount % 4 == 0 and frameCount >= 20 and windowFound == False:
                videoBox, accuracy = self.trackWindow(avg)
                print(accuracy)
                if accuracy > 70:
                    windowFound = True

                    boundingBoxNew = {
                        "top": self.optimalCoordinates["y"][0] + 100,
                        "left": self.optimalCoordinates["x"][0] + 960,
                        "width": self.optimalCoordinates["w"][0],
                        "height": self.optimalCoordinates["h"][0],
                    }

                    cv2.destroyAllWindows()
                    return boundingBoxNew

            else:
                videoBox = avg

            cv2.imshow("screen", np.array(videoBox))

            frameCount += 1

            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                cv2.destroyAllWindows()
                break

    # the actual screengrab function is this one

    def findVideo(self):

        time.sleep(2)
        # the resolution of my system is 1920 x 1080.
        # But because I am working on the same screen I'm goin to capture a smaller box
        # the 100 you're dropping from the top is in order to accomodate the menu bar.

        # setting first variables before use inside the loop
        frame1 = self.sct.grab(self.boundingBox)
        avg = np.float32(frame1)

        self.boundingBox = self.callTracker(frame1, self.boundingBox, avg)

    def takeScreenshot(self):
        # use this one from inside a loop.
        return np.array(self.sct.grab(self.boundingBox))

    def takeScreenshotByBox(self, timeInterval):
        # use this one if you need the loop outside of the main app
        frame1 = np.array(self.sct.grab(self.boundingBox))

        while True:

            time.sleep(timeInterval)

            frame1 = np.array(self.sct.grab(self.boundingBox))

            yield frame1

            if keyboard.is_pressed("q"):
                cv2.destroyAllWindows()
                break
