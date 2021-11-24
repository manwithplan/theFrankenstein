"""

1: Storage of hyper parameters

"""

# import libraries
import os
from os.path import dirname, abspath, realpath, join

# location variables
rootURL = dirname(dirname(abspath(__file__)))

musicSnippetsURL = os.path.join(rootURL, "theMusic", "theSnippets")
musicDBPath = "theDB"
musicFullDataBaseURL = os.path.join(rootURL, musicDBPath, "Database.csv")
musicSnippetsDataBaseURL = os.path.join(rootURL, musicDBPath, "DatabaseSplitted.csv")
musicMoodsDataBaseURL = os.path.join(rootURL, musicDBPath, "Cyanite.csv")

# global variables
shutterSpeed = 1  # the time between 2 imageGrabs

# detection coordinates
coordinatesHUD = [0.04, 0.36, 0.0, 1.0]
coordinatesDocking = [0.65, 0.80, 0.40, 0.60]
coordinatesConflict = [0.66, 0.95, 0.24, 0.38]
coordinatesSpeed = [0.74, 0.93, 0.55, 0.65]
coordinatesPlanet = [0.37, 0.63, 0.58, 0.68]
coordinatesShields = [0.67, 0.91, 0.64, 0.79]
coordinatesScaler = [0.0, 1, 0.85, 0.98]
coordinatesMiniMap = [0.65, 0.94, 0.37, 0.63]
coordinatesSupercruise = [0.3, 0.7, 0.77, 1.0]
