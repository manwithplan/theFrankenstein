import os
from typing import List, Set, Dict, Tuple, Optional, Union, Any, TypeVar, Bytes
import logging
import cv2
import numpy as np
import random
from tqdm import tqdm
from PIL import Image
import logging

import time


class imageConversion:
    """
    The imageConversion class contains a number helper functions for the processing of images. Both for
    the correct formatting for the training and testing of the neural nets, as the use within the app itself.

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

    getImage() :
        returns the current image

    getImageAsPIL() :
        returns the current image in PIL Image format

    loadImage() :
        Method that loads the current image from a given filename

    loadScreenshotImage() :
        Method that loads the current screenshot

    loadBMPImage() :
        reading the image into memory. Converts from BGRA to HSV color scale

    showImage() :
        show the image and wait until a keypress

    showImageInLoop():
        Method that shows the image and waits until a keypress.

    resizeImage() :
        Resizes to 128x128 pixels

    writeImage() :
        Write the image to the designated folder

    imageToGrayScale() :
        Convert image to grayscale

    filterImage() :
        Method that applies the correct filter to the image, and subtracting the mask.

    filterImageRed() :
        Method that applies the correct filter to the image, but only for red.

    applyAllFilters() :
        Applying all the filters consecutively on self.image, in HSV

    applyAllFiltersToRGB() :
        Applying all the filters consecutively on self.image, but in RGB


    """

    def __init__(self):
        super().__init__()
        self.image = None
        self.imageFiltered = None
        self.filters = {
            "docking": [[58, 0, 107], [122, 255, 255]],
            "hud": [[6, 185, 74], [72, 255, 255]],
            "hudBlue": [[83, 84, 49], [114, 255, 184]],
            "supercruise": [[12, 102, 0], [80, 255, 255]],
            "mining": [[107, 0, 90], [179, 65, 251]],
            "white": [[56, 0, 232], [179, 255, 255]],
        }
        self.filtersRed = {
            "lowRed": [[170, 167, 28], [179, 255, 255]],
            "highRed": [[0, 230, 0], [5, 255, 255]],
        }

    def getImage(self) -> object:
        """
        Method that returns the image
        """
        return self.image

    def getImageAsPIL(self, image) -> TypeVar("Image"):
        """
        Method that returns the current image as PIL
        """
        if image is None:
            toConvert = self.image
        else:
            toConvert = image

        img = cv2.cvtColor(toConvert, cv2.COLOR_BGR2RGB)

        return Image.fromarray(img)

    def loadImage(self, fileName: str) -> None:
        """
        Method that loads the current image from a given filename

        :fileName: str representing filename
        """
        loaded = fileName
        # bgr = cv2.cvtColor(loaded, cv2.COLOR_BGRA2BGR)
        bgr = loaded
        self.image = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        self.imageOriginal = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    def loadScreenshotImage(self, fileName: str) -> None:
        """
        Method that loads the current screenshot

        :fileName: str representing filename
        """
        loaded = fileName
        bgr = cv2.cvtColor(loaded, cv2.COLOR_BGRA2BGR)
        self.image = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        self.imageOriginal = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    def loadBMPImage(self, url: str, fileName: str) -> None:
        """
        reading the image into memory. Converts from BGRA to HSV color scale

        :url: path to file
        :fileName: str filename
        """

        loaded = cv2.imread(os.path.join(url, fileName), 1)
        bgr = cv2.cvtColor(loaded, cv2.COLOR_BGRA2BGR)
        self.image = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        self.imageOriginal = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    def showImage(self) -> None:
        """
        show the image and wait until a keypress
        """

        cv2.imshow("img", self.image)
        cv2.waitKey(0)

    def showImageInLoop(self, inputImage: TypeVar("Image")) -> None:
        """
        Method that shows the image and waits until a keypress.

        inputImage: PIL Image object to be shown.
        """
        if inputImage is None:
            img = self.image
        else:
            img = inputImage

        cv2.imshow("img", img)
        cv2.waitKey(1)

    def resizeImage(self) -> None:
        """
        Resizes to 128x128 pixels
        """
        self.image = cv2.resize(self.image, (128, 128), interpolation=cv2.INTER_AREA)

    def writeImage(self, url: str, toWrite: str) -> None:
        """
        Write the image to the designated folder

        :url; str reference to local path
        :toWrite: filename to be written.
        """
        cv2.imwrite(url, toWrite)

    def imageToGrayScale(self, image: TypeVar("Image")) -> TypeVar("Image"):
        """
        Convert image to grayscale

        :image: PIL Image to convert
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def filterImage(
        self, filter: List[float], image: TypeVar("Image")
    ) -> TypeVar("Image"):
        """
        Method that applies the correct filter to the image, and subtracting the mask.

        :filter: the filter to apply as a list of float values
        :image: PIL Image to apply filmter on
        :return: HSV filtered PIL Image
        """
        lowerRegion = np.array(self.filters[filter][0])
        upperRegion = np.array(self.filters[filter][1])

        # create and apply the mask
        mask = cv2.inRange(image, lowerRegion, upperRegion)
        return cv2.bitwise_and(image, image, mask=mask)

    def filterImageRed(
        self, filter1: List[float], filter2: List[float], image: TypeVar("Image")
    ) -> TypeVar("Image"):
        """
        red hsv value is tricky, because it 'wraps around the 0' meaning there is red from 0 to 10 as well as red from 350 to 360 if you look at it laike a circle.
        applying the correct filter to the image, and subtracting the mask.

        :filter1: the filter to apply as a list of float values
        :filter2: the filter to apply as a list of float values
        :image: PIL Image to apply filmter on
        :return: HSV filtered PIL Image
        """

        lowerRegion1 = np.array(filter1[0])
        upperRegion1 = np.array(filter1[1])
        lowerRegion2 = np.array(filter2[0])
        upperRegion2 = np.array(filter2[1])

        # create and apply the mask
        mask1 = cv2.inRange(image, lowerRegion1, upperRegion1)
        mask2 = cv2.inRange(image, lowerRegion2, upperRegion2)

        mask = mask1 + mask2

        return cv2.bitwise_and(image, image, mask=mask)

    def applyAllFilters(self) -> TypeVar("Image"):
        """
        Applying all the filters consecutively on self.image, in HSV

        :returns: A 6 channel image, where each channel holds 1 of the filtered results.
        """

        filteredImages = []
        for x in self.filters.keys():
            filtered = self.filterImage(x, self.image)
            filtered = self.imageToGrayScale(filtered)

            filteredImages.append(filtered)

        return (
            filteredImages[0] / 6
            + filteredImages[1] / 6
            + filteredImages[2] / 6
            + filteredImages[3] / 6
            + filteredImages[4] / 6
            + filteredImages[5] / 6
        )

    def applyAllFiltersToRGB(self) -> TypeVar("Image"):
        """
        Applying all the filters consecutively on self.image, but in RGB

        :returns: A 3 channel image, where each channel holds 1 of the filtered results.
        """

        filteredImages = []

        filtered = self.filterImageRed(
            self.filtersRed["lowRed"], self.filtersRed["highRed"], self.image
        )
        filtered = self.imageToGrayScale(filtered)

        filteredImages.append(filtered)

        for x in self.filters.keys():
            filtered = self.filterImage(x, self.image)
            filtered = self.imageToGrayScale(filtered)

            filteredImages.append(filtered)

        featureLayersCombined = cv2.merge(
            (
                filteredImages[0],
                cv2.add(filteredImages[2], filteredImages[3]),
                cv2.add(filteredImages[4], filteredImages[1]),
            )
        )

        return featureLayersCombined
