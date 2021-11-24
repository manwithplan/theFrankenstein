"""

The object detection class holds all the object detection algorithms that will be structured inside the detectionMain class.

"""

import numpy as np
import cv2
from matplotlib import pyplot as plt
import os
import random
from scipy import ndimage

from .imageConversion import imageConversion

class objectDetection():
    def __init__(self):
        super().__init__()

        # initialize an empy searchImage file
        self.searchImage = None

    def detectionHoughLinesHUD(self, inputImage, debugMode = False):
        anglesLeft = []
        anglesRight = []

        avgLeft = 0
        avgRight = 0

        screenAngle = 0

        edges = cv2.Canny(inputImage, 50, 150, apertureSize = 3)

        lines = cv2.HoughLines(edges, 1, np.pi/180, 150)
        try:
            for line in lines:
                rho,theta = line[0]
                if theta < 1.5:
                    anglesLeft.append(theta)
                else:
                    anglesRight.append(theta)

                if debugMode:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))
                    cv2.line(inputImage,(x1,y1),(x2,y2),(0,0,255),2)

            # averages are calculated in both directions to calculate the presence of the HUD
            avgLeft = sum(anglesLeft)/len(anglesLeft)
            avgRight = sum(anglesRight)/len(anglesRight)
            # screenAngle calculates the angle to which the screen can be rotated to line everything up.
            screenAngle = ( (avgLeft + avgRight) / 2 ) * 180 / 3.1415926 - 90

            #print('avgLeft : {:.2f} - avgRight : {:.2f} - distance : {:.2f} - screenAngle : {:.2f}'.format(avgLeft, avgRight, avgRight - avgLeft, screenAngle))

        except Exception as e:
            pass
        
        if debugMode:
            return [inputImage, avgRight - avgLeft, screenAngle]
        
        return [None, avgRight - avgLeft, screenAngle]
    
    def detectionHoughLines(self, inputImage, debugMode = False):

        edges = cv2.Canny(inputImage, 50, 150, apertureSize = 3)

        lines = cv2.HoughLines(edges, 1, np.pi/180, 150)
        try:
            for line in lines:
                rho,theta = line[0]

                if debugMode:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))
                    cv2.line(inputImage,(x1,y1),(x2,y2),(255,255,255),2)

        except Exception as e:
            pass
        
        if debugMode:
            return [inputImage, lines]
        
        return [None, lines]

    def detectionHoughLinesP(self, inputImage, debugMode = False):
        inputImageP = inputImage.copy()

        edges = cv2.Canny(inputImage, 50, 150, apertureSize = 3)

        # Probabilistic Line Transform
        linesP = cv2.HoughLinesP(edges, 1, np.pi / 180, 70, None, 50, 10)

        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                cv2.line(inputImageP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)

        return [inputImageP, linesP]

    def detectionHoughCircles(self, inputImage, debugMode = False):

        circles = cv2.HoughCircles(inputImage, cv2.HOUGH_GRADIENT, 1, 60, param1=200, param2=20, minRadius=0, maxRadius=0)

        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(inputImage,(i[0],i[1]),i[2],(255,255,255),2)
            # draw the center of the circle
            cv2.circle(inputImage,(i[0],i[1]),2,(255,255,255),3)

        return [inputImage, circles]
