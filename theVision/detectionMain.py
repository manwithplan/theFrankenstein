"""

detectionMain takes the filtered screenshots from visionMain as input and ties together all the algorithms 
to make each seperate detection. At the end of the logic tree it will return the current state.

the main function in this class does exactly that, by using a number of optimized functions for the different 
objects and state we try to detect. 

- stateLogic attempts to write a decision tree that takes into account several detection results. If no planet is 
detected but a docking screen is that means we are docking with a space station.

- runDetection: responsible for unpacking and structuring the inputs, calling the bulk of the detection functions
and organizing them and storing the results of the detection as flags to be interpreted in determining the gameState.

- cropWindow: local function used by the detection functions to select a Region Of Interest and decrease the workload

- detectionHUD: detect the presence of the HUD on the screen. This is done by detecting the lines of the 2 menu 
bars near the top of the window and calculating the angle. If the angle is within a margin of 
error of a predetermined angle we can confidently say that we are in-game because a HUD is detected. 

- detectionDocking: detects the presence of the docking screen that occurs after requesting clearance to dock. This is 
done by selecting ROI and detecting the blue color that is used for the message. If we then detect a 
few lines at a certain distance of one another and of a certain length we can detect the message.

- detectionConflict: selects the targeted ship icon and detects the amount of red pixels present. If this amount crosses a certain 
threshold we can somewhat confidently say the player is engaging an enemy ship.

- detectionSpeed: Detects the current speed of the player's ship. The trick here is to define a min and max very close at say 0 and 1 and allow the game 
to set them in real-time, if the player goes full speed a new max speed is set and the speed is calculated as a ratio between the min and 
max. More concretely we detect the area of the green speed bar which is convered by speed bars. 

- detectionPlanet: Detect the present of a different HUD that is only visible when near a planet in the game. The line to be detected 
is a vertical green line of a certain length.

- detectionShields: detecting the health level of the shields in game. Detecting the number of pixels of a blue color within 
the ROI of the players ship icon is the main mechanism. The game always starts with full shields, so we 
set that as a maximum and then always compare the current amount of pixels to it. The ratio between these 2 
give the percentage of shields currently left.

- detectionMinimap: Detecting the amount of hostiles, we filter the red colors from the ROI of the minimap in the middle of the 
HUD. When we dilate these pixels we come up with several 'blobs', and count them. The amount of blobs counted is 
equal to the amount of hostiles detected. 

- detectionSupercruise: When the player is in supercruise a number of grey vertical lines are shown on each side of the FOV. They 
slide into each other in a pseudo Doppler effect to tell the current speed. We simply cselect the POV and 
count the amount of lines we have, and if there are more than 2, to determine supercruise.

"""
import time
import numpy as np
from scipy import ndimage
import imutils
import cv2

from Settings.Settings import (
    coordinatesHUD,
    coordinatesDocking,
    coordinatesConflict,
    coordinatesSpeed,
    coordinatesPlanet,
    coordinatesShields,
    coordinatesScaler,
    coordinatesMiniMap,
    coordinatesSupercruise,
)


class detectionMain:
    def __init__(self):
        super().__init__()

        # initialize the inputImage variables
        self.inputGreen = None
        self.inputBlue = None
        self.inputRed = None
        self.inputWhite = None
        self.inputGray = None

        # initialize detection flags
        self.detectedHUD = False
        self.detectedDocking = False
        self.detectedConflict = False
        self.detectedPlanet = False
        self.detectedSupercruise = False

        # initialize numerical detection variables
        self.detectedSpeed = None
        self.lowSpeed = None
        self.highSpeed = None

        self.detectedShields = 0
        self.maxShields = 1
        self.minShields = 0

        self.detectedHostiles = 0

        # initialize gameState variables
        self.detectionState = False
        self.gameState = "None"
        self.gameStateList = ["None"] * 10
        self.gameStateAvg = "None"

        # debugging preview
        self.preview = None

    def stateLogic(self):
        # state detection is ran from inside run detection as a final step to get the current game state.
        if self.detectedHUD:

            self.detectionState = True

            if self.detectedConflict == True:
                if self.detectedHostiles > 2:

                    self.gameState = "conflictZone"

                else:

                    self.gameState = "conflictDogFight"

            elif self.detectedDocking == True:

                if self.detectedPlanet == True:

                    self.gameState = "planetaryLanding"

                else:

                    self.gameState = "docking"

            elif self.detectedSupercruise == True:

                self.gameState = "travel"

            elif self.detectedPlanet == True:

                if self.detectedSpeed > 0.95:

                    self.gameState = "canyonRunning"

                else:

                    self.gameState = "planetaryExploration"

            else:

                self.gameState = "slowTravel"

        elif self.detectionState == True:

            self.gameState = "Menu"

        else:

            self.gameState = "False"

        self.gameStateList.pop(0)
        self.gameStateList.append(self.gameState)
        self.gameStateAvg = max(set(self.gameStateList), key=self.gameStateList.count)

    def runDetection(self, inputs, timeIt=False):
        # responsible for unpacking and structuring the inputs, calling the bulk of the detection functions
        # and organizing them and storing the results of the detection as flags to be interpreted in determining the gameState.

        if timeIt:
            # initialize some timing vars
            HUDTime = 0
            rotationTime = 0
            dockingTime = 0
            conflictTime = 0
            speedTime = 0
            planetTime = 0
            shieldsTime = 0
            miniMapTime = 0
            supercruiseTime = 0

        # gather the images from input
        self.inputGreen = cv2.cvtColor(inputs[0], cv2.COLOR_BGR2GRAY)
        self.inputBlue = cv2.cvtColor(inputs[1], cv2.COLOR_BGR2GRAY)
        self.inputRed = cv2.cvtColor(inputs[2], cv2.COLOR_BGR2GRAY)
        self.inputWhite = cv2.cvtColor(inputs[3], cv2.COLOR_BGR2GRAY)
        self.inputGray = cv2.cvtColor(inputs[4], cv2.COLOR_BGR2GRAY)

        start_time = time.time()

        # running the HUD detecting algo:
        _, screenAngle = self.detectionHUD(
            self.cropWindow(self.inputGreen, coordinatesHUD)
        )
        HUDTime = time.time() - start_time

        if self.detectedHUD:

            start_time = time.time()
            self.inputGreen = imutils.rotate(self.inputGreen, screenAngle)
            self.inputBlue = imutils.rotate(self.inputBlue, screenAngle)
            self.inputRed = imutils.rotate(self.inputRed, screenAngle)
            self.inputWhite = imutils.rotate(self.inputWhite, screenAngle)
            self.inputGray = imutils.rotate(self.inputGray, screenAngle)
            rotationTime = time.time() - start_time

            if timeIt:
                start_time = time.time()
                # running the Docking detection algo w time:
                _ = self.detectionDocking(
                    self.cropWindow(self.inputBlue, coordinatesDocking)
                )
                dockingTime = time.time() - start_time

                start_time = time.time()
                # running conflict detection algo w time:
                _ = self.detectionConflict(
                    self.cropWindow(self.inputRed, coordinatesConflict)
                )
                conflictTime = time.time() - start_time

                start_time = time.time()
                # running speed detection algo w time:
                _ = self.detectionSpeed(
                    self.cropWindow(self.inputGreen, coordinatesSpeed)
                )
                speedTime = time.time() - start_time

                start_time = time.time()
                # running proximity to planet detection algo w time:
                _ = self.detectionPlanet(
                    self.cropWindow(self.inputGreen, coordinatesPlanet)
                )
                planetTime = time.time() - start_time

                start_time = time.time()
                # running proximity to shield detection algo w time:
                _ = self.detectionShields(
                    self.cropWindow(self.inputBlue, coordinatesShields)
                )
                shieldsTime = time.time() - start_time

                start_time = time.time()
                # running proximity to minimap detection algo w time:
                _ = self.detectionMiniMap(
                    [
                        self.cropWindow(self.inputRed, coordinatesMiniMap),
                        self.cropWindow(self.inputWhite, coordinatesMiniMap),
                    ]
                )
                miniMapTime = time.time() - start_time

                start_time = time.time()
                # running proximity to supercruise detection algo w time:
                _ = self.detectionSupercruise(
                    self.cropWindow(self.inputGray, coordinatesSupercruise)
                )
                supercruiseTime = time.time() - start_time

            else:

                # running the Docking detection algo:
                _ = self.detectionDocking(
                    self.cropWindow(self.inputBlue, coordinatesDocking)
                )

                # running conflict detection algo:
                _ = self.detectionConflict(
                    self.cropWindow(self.inputRed, coordinatesConflict)
                )

                # running speed detection algo:
                _ = self.detectionSpeed(
                    self.cropWindow(self.inputGreen, coordinatesSpeed)
                )

                # running proximity to planet detection algo:
                _ = self.detectionPlanet(
                    self.cropWindow(self.inputGreen, coordinatesPlanet)
                )

                # running proximity to shield detection algo:
                _ = self.detectionShields(
                    self.cropWindow(self.inputBlue, coordinatesShields)
                )

                # running proximity to minimap detection algo:
                _ = self.detectionMiniMap(
                    [
                        self.cropWindow(self.inputRed, coordinatesMiniMap),
                        self.cropWindow(self.inputWhite, coordinatesMiniMap),
                    ]
                )

                # running proximity to supercruise detection algo w time:
                _ = self.detectionSupercruise(
                    self.cropWindow(self.inputGray, coordinatesSupercruise)
                )

        self.stateLogic()

        if timeIt:
            totalTime = (
                HUDTime
                + rotationTime
                + conflictTime
                + speedTime
                + planetTime
                + shieldsTime
                + miniMapTime
                + supercruiseTime
            )
            print(
                " \n state : {} - total time : {:.3f} \n HUD : {} in {:.3f}s \n rotation in {:.3f}s \n docking : {} in {:.3f}s \n conflict : {} in {:.3f}s \n speed : {:.2f} in {:.3f}s \n planet : {} in {:.3f}s \n shields : {:.2f} in {:.3f}s \n hostiles : {} in {:.3f}s \n supercruise : {} in {:.3f}s".format(
                    self.gameStateList,
                    totalTime,
                    self.detectedHUD,
                    HUDTime,
                    rotationTime,
                    self.detectedDocking,
                    dockingTime,
                    self.detectedConflict,
                    conflictTime,
                    self.detectedSpeed,
                    speedTime,
                    self.detectedPlanet,
                    planetTime,
                    self.detectedShields,
                    shieldsTime,
                    self.detectedHostiles,
                    miniMapTime,
                    self.detectedSupercruise,
                    supercruiseTime,
                ),
                end="\r",
            )

    def cropWindow(self, inputImage, coordinates):
        # local function used by the detection functions to select a Region Of Interest and decrease the workload
        y1 = int(inputImage.shape[0] * coordinates[0])
        y2 = int(inputImage.shape[0] * coordinates[1])
        x1 = int(inputImage.shape[1] * coordinates[2])
        x2 = int(inputImage.shape[1] * coordinates[3])
        return inputImage[y1:y2, x1:x2]

    def detectionHUD(self, inputImage, searchArea=None, debugMode=False):
        # detect the presence of the HUD on the screen. This is done by detecting the lines of the 2 menu
        # bars near the top of the window and calculating the angle. If the angle is within a margin of
        # error of a predetermined angle we can confidently say that we are in-game because a HUD is detected.

        anglesLeft = []
        anglesRight = []

        avgLeft = 0
        avgRight = 0

        screenAngle = 0

        edges = cv2.Canny(inputImage, 50, 150, apertureSize=3)

        lines = cv2.HoughLines(edges, 1, np.pi / 180, 150)

        try:
            for line in lines:
                rho, theta = line[0]
                if theta < 1.5:
                    anglesLeft.append(theta)
                else:
                    anglesRight.append(theta)

                if debugMode:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * (a))
                    cv2.line(inputImage, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # averages are calculated in both directions to calculate the presence of the HUD
            avgLeft = sum(anglesLeft) / len(anglesLeft)
            avgRight = sum(anglesRight) / len(anglesRight)
            avgDistance = avgRight - avgLeft
            # screenAngle calculates the angle to which the screen can be rotated to line everything up.
            screenAngle = ((avgLeft + avgRight) / 2) * 180 / 3.1415926 - 90

            # print('avgLeft : {:.2f} - avgRight : {:.2f} - distance : {:.2f} - screenAngle : {:.2f}'.format(avgLeft, avgRight, avgRight - avgLeft, screenAngle))

            # implementing logic that makes the detection from the raw data
            if avgDistance >= 0.3 and avgDistance <= 0.43:
                self.detectedHUD = True
            else:
                self.detectedHUD = False

        except Exception as e:
            self.detectedHUD = False

        if debugMode:
            return [inputImage, screenAngle]

        return [None, screenAngle]

    def detectionDocking(self, inputImage, debugMode=False):
        # detects the presence of the docking screen that occurs after requesting clearance to dock. This is
        # done by selecting ROI and detecting the blue color that is used for the message. If we then detect a
        # few lines at a certain distance of one another and of a certain length we can detect the message

        # initialiing a variable to store how many matches are found.
        matches = 0

        try:

            edges = cv2.Canny(inputImage, 50, 150, apertureSize=3)

            # Probabilistic Line Transform
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 70, None, 50, 10)

            if debugMode:
                if lines is not None:
                    for i in range(0, len(lines)):
                        l = lines[i][0]
                        cv2.line(
                            inputImage,
                            (l[0], l[1]),
                            (l[2], l[3]),
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA,
                        )

            for line in lines:
                distance = line[0, 1] - line[0, 3]
                if distance < 3:
                    if line[0, 2] - line[0, 0] > 100:
                        matches += 1

        except Exception as e:
            pass

        if matches >= 2:
            self.detectedDocking = True
        else:
            self.detectedDocking = False

        if debugMode:
            return inputImage

        return None

    def detectionConflict(self, inputImage, debugMode=False):
        # selects the targeted ship icon and detects the amount of red pixels present. If this amount crosses a certain
        # threshold we can somewhat confidently say the player is engaging an enemy ship.

        conflictThresholdMin = 4000
        conflictThresholdMax = 11000

        try:

            zeros = cv2.countNonZero(inputImage)

            if zeros > conflictThresholdMin and zeros < conflictThresholdMax:
                self.detectedConflict = True
            else:
                self.detectedConflict = False

        except Exception as e:
            pass

        if debugMode:
            return inputImage

        return None

    def detectionSpeed(self, inputImage, debugMode=False):
        # detects the current speed of the player's ship. The trick here is to define a min and max very close at say 0 and 1 and allow the game
        # to set them in real-time, if the player goes full speed a new max speed is set and the speed is calculated as a ratio between the min and
        # max. More concretely we detect the area of the green speed bar which is convered by speed bars.

        try:
            ret, thresh = cv2.threshold(inputImage, 200, 255, 0)
            contours, hierarchy = cv2.findContours(
                thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(inputImage, contours, -1, (255, 255, 255), 1)

            c = cv2.contourArea(max(contours, key=cv2.contourArea))

            if self.highSpeed is None:
                self.lowSpeed = c - 1
                self.highSpeed = c + 1
            elif c < self.lowSpeed:
                self.lowSpeed = c
            elif c > self.highSpeed:
                self.highSpeed = c

            self.detectedSpeed = (c - self.lowSpeed) / (self.highSpeed - self.lowSpeed)

        except:
            pass

        if debugMode:
            return inputImage

        return None

    def detectionPlanet(self, inputImage, debugMode=False):
        # Detect the present of a different HUD that is only visible when near a planet in the game. The line to be detected
        # is a vertical green line of a certain length.
        matches = 0

        try:

            edges = cv2.Canny(inputImage, 50, 150, apertureSize=3)

            # Probabilistic Line Transform
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, None, 50, 20)

            if debugMode:
                if lines is not None:
                    for i in range(0, len(lines)):
                        l = lines[i][0]
                        cv2.line(
                            inputImage,
                            (l[0], l[1]),
                            (l[2], l[3]),
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA,
                        )

            for line in lines:
                distance = line[0, 0] - line[0, 2]
                if abs(distance) < 3:
                    if abs(line[0, 3] - line[0, 1]) > 50:
                        matches += 1
                        # print(distance, abs(line[0,3] - line[0,1]), matches)

        except Exception as e:
            pass

        if matches >= 2:
            self.detectedPlanet = True
        else:
            self.detectedPlanet = False

        if debugMode:
            return inputImage

        return None

    def detectionShields(self, inputImage, debugMode=False):
        # detecting the health level of the shields in game. Detecting the number of pixels of a blue color within
        # the ROI of the players ship icon is the main mechanism. The game always starts with full shields, so we
        # set that as a maximum and then always compare the current amount of pixels to it. The ratio between these 2
        # give the percentage of shields currently left.

        try:

            zeros = cv2.countNonZero(inputImage)

            if zeros > self.maxShields:
                self.maxShields = zeros

            self.detectedShields = zeros / self.maxShields

        except:
            pass

        if debugMode:
            return inputImage

        return None

    def detectionMiniMap(self, inputImages, debugMode=False):
        # Detecting the amount of hostiles, we filter the red colors from the ROI of the minimap in the middle of the
        # HUD. When we dilate these pixels we come up with several 'blobs', and count them. The amount of blobs counted is
        # equal to the amount of hostiles detected.
        matches = 0

        try:

            _, threshRed = cv2.threshold(inputImages[0], 190, 255, cv2.THRESH_BINARY)
            _, threshWhite = cv2.threshold(inputImages[1], 10, 255, cv2.THRESH_BINARY)

            combined = cv2.bitwise_or(threshRed, threshWhite)

            # blur = cv2.bilateralFilter(combined,25,75,75)
            kernel = np.ones((6, 6), np.uint8)
            blur = cv2.dilate(combined, kernel, iterations=1)

            contours, _ = cv2.findContours(blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # cv2.drawContours(inputImage, contours, -1, (255,255,255), 1)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 50 <= area:

                    if debugMode:
                        combined = cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
                        cv2.drawContours(combined, cnt, -1, (0, 0, 255), 3)

                    matches += 1

        except Exception as e:
            pass

        hostiles = matches - 2
        if hostiles < 0:
            hostiles = 0

        self.detectedHostiles = matches - 2

        if debugMode:
            return combined

        return None

    def detectionSupercruise(self, inputImage, debugMode=False):
        # When the player is in supercruise a number of grey vertical lines are shown on each side of the FOV. They
        # slide into each other in a pseudo Doppler effect to tell the current speed. We simply cselect the POV and
        # count the amount of lines we have, and if there are more than 2, to determine supercruise.

        matches = 0
        self.detectedSupercruise = False

        try:

            _, thresh = cv2.threshold(inputImage, 40, 255, cv2.THRESH_BINARY)

            edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

            lines = cv2.HoughLines(edges, 1, np.pi / 180, 20)

            for line in lines:

                rho, theta = line[0]
                if -0.1 <= theta <= 0.1:
                    matches += 1

                if debugMode:
                    inputImage = cv2.cvtColor(inputImage, cv2.COLOR_GRAY2BGR)

                    if lines is not None:
                        for i in range(0, len(lines)):
                            rho = lines[i][0][0]
                            theta = lines[i][0][1]
                            a = np.cos(theta)
                            b = np.sin(theta)
                            x0 = a * rho
                            y0 = b * rho
                            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
                            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
                            cv2.line(inputImage, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)

        except:
            pass

        if matches >= 1:
            self.detectedSupercruise = True

        if debugMode:
            return inputImage

        return None
