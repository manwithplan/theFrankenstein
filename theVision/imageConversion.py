"""

The following class contains all the code for the processing of images. Both for independent use, 
as the correct formatting for the training and testing of the neural nets.

"""

import os
import cv2
import numpy as np
import random
from tqdm import tqdm
from PIL import Image

import time

class imageConversion():

    def __init__(self):
        super().__init__()
        self.image = None
        self.imageFiltered = None
        self.filters = {
            'docking' : [[58, 0, 107], [122, 255, 255]] , 
            'hud' : [[6, 185, 74], [72, 255, 255]] , 
            'hudBlue' : [[83, 84, 49], [114, 255, 184]] , 
            'supercruise' : [[12,102,0], [80, 255, 255]] , 
            'mining' : [[107, 0, 90], [179, 65, 251]] ,
            'white' : [[56, 0, 232], [179, 255, 255]]
        }
        self.filtersRed = {
            'lowRed' : [[170, 167, 28], [179, 255, 255]],
            'highRed' : [[0, 230, 0], [5, 255, 255]]
        }

    def getImage(self):
        return self.image

    def getImageAsPIL(self, image):
        if image is None:
            toConvert = self.image
        else:
            toConvert = image

        img = cv2.cvtColor(toConvert, cv2.COLOR_BGR2RGB)

        return Image.fromarray(img)

    def loadImage(self, fileName):
        loaded = fileName
        #bgr = cv2.cvtColor(loaded, cv2.COLOR_BGRA2BGR)
        bgr = loaded
        self.image = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        self.imageOriginal = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    def loadScreenshotImage(self, fileName):
        loaded = fileName
        bgr = cv2.cvtColor(loaded, cv2.COLOR_BGRA2BGR)
        self.image = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        self.imageOriginal = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    def loadBMPImage(self, url, fileName):
        # reading the image into memory, the 1 stands for color. Converts from BGRA to HSV color scale
        loaded = cv2.imread(os.path.join(url,fileName),1)
        bgr = cv2.cvtColor(loaded, cv2.COLOR_BGRA2BGR)
        self.image = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        self.imageOriginal = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    def showImage(self):
        # show the image and wait until a keypress
        cv2.imshow('img', self.image)
        cv2.waitKey(0)

    def showImageInLoop(self, inputImage):
        if inputImage is None:
            img = self.image
        else: 
            img = inputImage

        # show the image and wait until a keypress
        cv2.imshow('img', img)
        cv2.waitKey(1)

    def resizeImage(self):
        # resizes to 128x128 pixels, optimal for nn's
        self.image = cv2.resize(self.image, (128,128), interpolation = cv2.INTER_AREA)

    def writeImage(self, url, toWrite):
        # write the image to the designated folder
        cv2.imwrite(url, toWrite)

    def imageToGrayScale(self, image):
        # does what it says it does
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def filterImage(self, filter, image):
        # applying the correct filter to the image, and subtracting the mask.
        lowerRegion = np.array(self.filters[filter][0])
        upperRegion = np.array(self.filters[filter][1])

        # create and apply the mask
        mask = cv2.inRange(image, lowerRegion, upperRegion)
        return cv2.bitwise_and(image, image, mask=mask)

    def filterImageRed(self, filter1, filter2, image):
        # red hsv value is tricky, because it 'wraps around the 0' meaning there is red from 0 to 10 as well as red from 350 to 360 if you look at it laike a circle.
        # applying the correct filter to the image, and subtracting the mask.
        lowerRegion1 = np.array(filter1[0])
        upperRegion1 = np.array(filter1[1])
        lowerRegion2 = np.array(filter2[0])
        upperRegion2 = np.array(filter2[1])

        # create and apply the mask
        mask1 = cv2.inRange(image, lowerRegion1, upperRegion1)
        mask2 = cv2.inRange(image, lowerRegion2, upperRegion2)

        mask = mask1 + mask2

        return cv2.bitwise_and(image, image, mask=mask)

    def applyAllFilters(self):
        # applying all the filters consecutively.

        filteredImages = []
        for x in self.filters.keys():
            filtered = self.filterImage(x, self.image)
            filtered = self.imageToGrayScale(filtered)

            filteredImages.append(filtered)

        return filteredImages[0]/6 + filteredImages[1]/6 + filteredImages[2]/6 + filteredImages[3]/6 + filteredImages[4]/6 + filteredImages[5]/6
        
    def applyAllFiltersToRGB(self):
        # applying all the filters consecutively.

        filteredImages = []

        filtered = self.filterImageRed(self.filtersRed['lowRed'], self.filtersRed['highRed'], self.image)
        filtered = self.imageToGrayScale(filtered)

        filteredImages.append(filtered)

        for x in self.filters.keys():
            filtered = self.filterImage(x, self.image)
            filtered = self.imageToGrayScale(filtered)

            filteredImages.append(filtered)

        featureLayersCombined = cv2.merge( ( filteredImages[0], cv2.add(filteredImages[2], filteredImages[3]),  cv2.add(filteredImages[4], filteredImages[1]) ) )

        return featureLayersCombined
