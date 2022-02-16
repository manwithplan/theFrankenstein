import time
import numpy as np
from scipy import ndimage
import imutils
import cv2
from typing import List, Set, Dict, Tuple, Optional, Union, Any, TypeVar, Bytes
import logging

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
    """
    DetectionMain takes the filtered screenshots from visionMain as input and ties together all the algorithms
    to make each seperate detection. At the end of the logic tree it will return the current state.

    the main function in this class does exactly that, by using a number of optimized functions for the different
    objects and state we try to detect.

    ...

    Attributes
    ----------
    gameState : str
        string representing the current gamestate

    preview : Image
        debuggin image.

    Methods
    -------

    stateLogic() :
        attempts to write a decision tree that takes into account several detection results. If no planet is
        detected but a docking screen is that means we are docking with a space station.

    runDetection() :
        responsible for unpacking and structuring the inputs, calling the bulk of the detection functions
        and organizing them and storing the results of the detection as flags to be interpreted in determining the gameState.

    cropWindow() :
        local function used by the detection functions to select a Region Of Interest and decrease the workload

    detectionHUD() :
        detect the presence of the HUD on the screen. This is done by detecting the lines of the 2 menu
        bars near the top of the window and calculating the angle. If the angle is within a margin of
        error of a predetermined angle we can confidently say that we are in-game because a HUD is detected.

    detectionDocking() :
        detects the presence of the docking screen that occurs after requesting clearance to dock. This is
        done by selecting ROI and detecting the blue color that is used for the message. If we then detect a
        few lines at a certain distance of one another and of a certain length we can detect the message.

    detectionConflict() :
        selects the targeted ship icon and detects the amount of red pixels present. If this amount crosses a certain
        threshold we can somewhat confidently say the player is engaging an enemy ship.

    detectionSpeed() :
        Detects the current speed of the player's ship. The trick here is to define a min and max very close at say 0 and 1 and allow the game
        to set them in real-time, if the player goes full speed a new max speed is set and the speed is calculated as a ratio between the min and
        max. More concretely we detect the area of the green speed bar which is convered by speed bars.

    detectionPlanet() :
        Detect the present of a different HUD that is only visible when near a planet in the game. The line to be detected
        is a vertical green line of a certain length.

    detectionShields() :
        detecting the health level of the shields in game. Detecting the number of pixels of a blue color within
        the ROI of the players ship icon is the main mechanism. The game always starts with full shields, so we
        set that as a maximum and then always compare the current amount of pixels to it. The ratio between these 2
        give the percentage of shields currently left.

    detectionMinimap() :
        Detecting the amount of hostiles, we filter the red colors from the ROI of the minimap in the middle of the
        HUD. When we dilate these pixels we come up with several 'blobs', and count them. The amount of blobs counted is
        equal to the amount of hostiles detected.

    detectionSupercruise() :
        When the player is in supercruise a number of grey vertical lines are shown on each side of the FOV. They
        slide into each other in a pseudo Doppler effect to tell the current speed. We simply cselect the POV and
        count the amount of lines we have, and if there are more than 2, to determine supercruise.
    """

    def __init__(self) -> None:
        super().__init__()

        # initalize logger object
        self.logger: object = logging.getLogger(__name__)
        self.logger.info("detectionMain object initialized")

        # initialize the inputImage variables
        self.inputGreen: TypeVar("Image") = None
        self.inputBlue: TypeVar("Image") = None
        self.inputRed: TypeVar("Image") = None
        self.inputWhite: TypeVar("Image") = None
        self.inputGray: TypeVar("Image") = None

        # initialize detection flags
        self.detectedHUD: bool = False
        self.detectedDocking: bool = False
        self.detectedConflict: bool = False
        self.detectedPlanet: bool = False
        self.detectedSupercruise: bool = False

        # initialize numerical detection variables
        self.detectedSpeed: Union[None, float] = None
        self.lowSpeed: Union[None, float] = None
        self.highSpeed: Union[None, float] = None

        self.detectedShields: Union[int, float] = 0
        self.maxShields: Union[int, float] = 1
        self.minShields: Union[int, float] = 0

        self.detectedHostiles: int = 0

        # initialize gameState variables
        self.detectionState: bool = False
        self.gameState: str = "None"
        self.gameStateList: List[str] = ["None"] * 10
        self.gameStateAvg: str = "None"

        # debugging preview
        self.preview: TypeVar("Image") = None

    def stateLogic(self) -> None:
        """
        Hierarchical tree structure determining the eventual gamestate based on the flags detected.
        """

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

        # perform logging operations
        self.logger.debug(f"stateLogic method called")
        self.logger.debug(f"self.gameState : {self.gameState}")

    def runDetection(self, inputs: TypeVar("Image"), timeIt: bool = False) -> None:
        """
        Method responsible for unpacking and structuring the inputs, calling the bulk of the detection functions
        and organizing them and storing the results of the detection as flags to be interpreted in determining the gameState.

        :inputs: screenshot grabbed by screenGrab module.
        :timeIt: flag to control whether functions are timed for debugging.
        """

        if timeIt:
            # initialize some timing vars
            HUDTime: float = 0
            rotationTime: float = 0
            dockingTime: float = 0
            conflictTime: float = 0
            speedTime: float = 0
            planetTime: float = 0
            shieldsTime: float = 0
            miniMapTime: float = 0
            supercruiseTime: float = 0

        # gather the images from input
        self.inputGreen: TypeVar("Image") = cv2.cvtColor(inputs[0], cv2.COLOR_BGR2GRAY)
        self.inputBlue: TypeVar("Image") = cv2.cvtColor(inputs[1], cv2.COLOR_BGR2GRAY)
        self.inputRed: TypeVar("Image") = cv2.cvtColor(inputs[2], cv2.COLOR_BGR2GRAY)
        self.inputWhite: TypeVar("Image") = cv2.cvtColor(inputs[3], cv2.COLOR_BGR2GRAY)
        self.inputGray: TypeVar("Image") = cv2.cvtColor(inputs[4], cv2.COLOR_BGR2GRAY)

        start_time = time.time()

        # running the HUD detecting algo:
        _, screenAngle = self.detectionHUD(
            self.cropWindow(self.inputGreen, coordinatesHUD)
        )
        HUDTime = time.time() - start_time

        if not self.detectedHUD:

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
                    self.cropWindow(self.inputRed, coordinatesConflict),
                    self.cropWindow(self.inputRed, coordinatesMiniMap),
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
            # perform logging operations
            self.logger.debug(f"runDetection method called")
            self.logger.debug(
                f"state : {self.gameStateList} - total time : {totalTime} HUD : {self.detectedHUD} in {HUDTime}s rotation in {rotationTime}s"
            )
            self.logger.debug(
                f"docking : {self.detectedDocking} in {dockingTime}s conflict : {self.detectedConflict} in {conflictTime}s speed : {self.detectedSpeed} in {speedTime}s"
            )
            self.logger.debug(
                f"planet : {self.detectedPlanet} in {planetTime}s shields : {self.detectedShields} in {shieldsTime}s hostiles : {self.detectedHostiles} in {miniMapTime}s supercruise : {self.detectedSupercruise} in {supercruiseTime}s"
            )

    def cropWindow(
        self, inputImage: TypeVar("Image"), coordinates: List[int]
    ) -> TypeVar("Image"):
        """
        local function used by the detection functions to select a Region Of Interest and decrease the workload

        :inputImage: PIL Image no be cropped
        :coordinates: the coordinates of the ROI we want to crop
        :return: cropped PIL Image
        """

        y1: int = int(inputImage.shape[0] * coordinates[0])
        y2: int = int(inputImage.shape[0] * coordinates[1])
        x1: int = int(inputImage.shape[1] * coordinates[2])
        x2: int = int(inputImage.shape[1] * coordinates[3])
        return inputImage[y1:y2, x1:x2]

    def detectionHUD(
        self, inputImage: TypeVar("Image"), debugMode: bool = False
    ) -> List[TypeVar("Image"), float]:
        """
        detect the presence of the HUD on the screen. This is done by detecting the lines of the 2 menu
        bars near the top of the window and calculating the angle. If the angle is within a margin of
        error of a predetermined angle we can confidently say that we are in-game because a HUD is detected.

        inputImage: PIL Image to be processed
        debugMode: Flag representing debugging or not.
        """

        anglesLeft: List[float] = []
        anglesRight: List[float] = []

        avgLeft: float = 0
        avgRight: float = 0

        screenAngle: float = 0

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

            # implementing logic that makes the detection from the raw data
            if avgDistance >= 0.3 and avgDistance <= 0.5:
                self.detectedHUD = True
            else:
                self.detectedHUD = False

        except Exception as e:
            self.detectedHUD = False

        # perform logging operations
        self.logger.debug(f"detectionHUD method called, {self.detectedHUD}")
        self.logger.debug(
            f"avgLeft : {avgLeft} - avgRight : {avgRight} - distance : {avgRight - avgLeft} - screenAngle : {screenAngle}"
        )

        if debugMode:
            return [inputImage, screenAngle]

        return [None, screenAngle]

    def detectionDocking(
        self, inputImage: TypeVar("Image"), debugMode: bool = False
    ) -> Union[None, TypeVar("Image")]:
        """
        Detects the presence of the docking screen that occurs after requesting clearance to dock. This is
        done by selecting ROI and detecting the blue color that is used for the message. If we then detect a
        few lines at a certain distance of one another and of a certain length we can detect the message

        :inputImage: PIL Image to be processed
        :debugMode: Flag representing debugging or not.
        :return: None if not debugging, otherwise the editid Image object.
        """

        # initialiing a variable to store how many matches are found.
        matches: int = 0

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

        self.logger.debug(f"detectedDocking method called, {self.detectedDocking}")

        if debugMode:
            return inputImage

        return None

    def detectionConflict(
        self,
        inputImage: TypeVar("Image"),
        inputImageNormalize: TypeVar("Image"),
        debugMode: bool = False,
    ) -> Union[None, TypeVar("Image")]:
        """
        Selects the targeted ship icon and detects the amount of red pixels present. If this amount crosses a certain
        threshold we can somewhat confidently say the player is engaging an enemy ship. The second input is there to
        normalize the general scale of red, because false positives are detected when in a certain angle of a sun.

        :inputImage: PIL Image to be processed
        :inputImageNormalize: PIL Image that is used to normalize color variance.
        :debugMode: Flag representing debugging or not.
        :return: None if not debugging, otherwise the editid Image object.
        """
        try:

            zeros_in_area: int = cv2.countNonZero(inputImage)
            zeros_in_test: int = cv2.countNonZero(inputImageNormalize)

            if zeros_in_test > 20000:
                conflictThresholdMin = 9000

            else:
                conflictThresholdMin = 5000

            if zeros_in_area > conflictThresholdMin:
                self.detectedConflict = True
            else:
                self.detectedConflict = False

        except Exception as e:
            pass

        self.logger.debug(f"detectionConflict method called, {self.detectionConflict}")
        try:
            self.logger.debug(
                f"zeros : {zeros_in_area} - test : {zeros_in_test} - ratio : {zeros_in_area/zeros_in_test}"
            )
        except ZeroDivisionError:
            pass

        if debugMode:

            return inputImage

        return None

    def detectionSpeed(
        self, inputImage: TypeVar("Image"), debugMode: bool = False
    ) -> Union[None, TypeVar("Image")]:
        """
        detects the current speed of the player's ship. The trick here is to define a min and max very close at say 0 and 1 and allow the game
        to set them in real-time, if the player goes full speed a new max speed is set and the speed is calculated as a ratio between the min and
        max. More concretely we detect the area of the green speed bar which is convered by speed bars.

        :inputImage: PIL Image to be processed
        :debugMode: Flag representing debugging or not.
        :return: None if not debugging, otherwise the edited Image object.
        """

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

        # perform logging operations
        self.logger.debug(f"detectionSpeed method called, {self.detectionSpeed}")

        if debugMode:
            return inputImage

        return None

    def detectionPlanet(
        self, inputImage: TypeVar("Image"), debugMode: bool = False
    ) -> Union[None, TypeVar("Image")]:
        """
        Detect the present of a different HUD that is only visible when near a planet in the game. The line to be detected
        is a vertical green line of a certain length.

        :inputImage: PIL Image to be processed
        :debugMode: Flag representing debugging or not.
        :return: None if not debugging, otherwise the edited Image object.
        """

        matches: int = 0

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

        # perform logging operations
        self.logger.debug(f"detectionPlanet method called, {self.detectionPlanet}")

        if debugMode:
            return inputImage

        return None

    def detectionShields(
        self, inputImage: TypeVar("Image"), debugMode: bool = False
    ) -> Union[None, TypeVar("Image")]:
        """
        Detecting the health level of the shields in game. Detecting the number of pixels of a blue color within
        the ROI of the players ship icon is the main mechanism. The game always starts with full shields, so we
        set that as a maximum and then always compare the current amount of pixels to it. The ratio between these 2
        give the percentage of shields currently left.

        :inputImage: PIL Image to be processed
        :debugMode: Flag representing debugging or not.
        :return: None if not debugging, otherwise the edited Image object.
        """

        try:

            zeros: int = cv2.countNonZero(inputImage)

            if zeros > self.maxShields:
                self.maxShields = zeros

            self.detectedShields = zeros / self.maxShields

        except:
            pass

        # perform logging operations
        self.logger.debug(f"detectionShields method called, {self.detectionShields}")
        self.logger.debug(f"zeros, {zeros}")

        if debugMode:
            return inputImage

        return None

    def detectionMiniMap(
        self, inputImages: TypeVar("Image"), debugMode: bool = False
    ) -> Union[None, TypeVar("Image")]:
        """
        Detecting the amount of hostiles, we filter the red colors from the ROI of the minimap in the middle of the
        HUD. When we dilate these pixels we come up with several 'blobs', and count them. The amount of blobs counted is
        equal to the amount of hostiles detected.

        :inputImage: PIL Image to be processed
        :debugMode: Flag representing debugging or not.
        :return: None if not debugging, otherwise the edited Image object.
        """
        matches: int = 0

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

        # perform logging operations
        self.logger.debug(f"detectionMiniMap method called, {self.detectionMiniMap}")
        self.logger.debug(f"area, {area}")

        if debugMode:
            return combined

        return None

    def detectionSupercruise(
        self, inputImage: TypeVar("Image"), debugMode: bool = False
    ) -> Union[None, TypeVar("Image")]:
        """
        When the player is in supercruise a number of grey vertical lines are shown on each side of the FOV. They
        slide into each other in a pseudo Doppler effect to tell the current speed. We simply cselect the POV and
        count the amount of lines we have, and if there are more than 2, to determine supercruise.

        :inputImage: PIL Image to be processed
        :debugMode: Flag representing debugging or not.
        :return: None if not debugging, otherwise the edited Image object.
        """

        matches: int = 0
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

        # perform logging operations
        self.logger.debug(
            f"detectedSupercruise method called, {self.detectedSupercruise}"
        )
        self.logger.debug(f"matches, {matches}")

        if debugMode:
            return inputImage

        return None
