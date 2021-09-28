'''

1: Storage of hyper parameters

'''

# import libraries
import os
from os.path import dirname, abspath, realpath, join

# location variables
rootURL = dirname( dirname(abspath(__file__)) )
musicFullURL = r'C:\Users\aubin\Desktop\OmniPhony\Music\MusOpen\FilesSplitted'
musicSnippetsURL = r'C:\Users\aubin\Desktop\OmniPhony\Music\MusOpen\Files'
musicFullDataBaseURL = os.path.join(rootURL, "Database.csv")
musicSnippetsDataBaseURL = os.path.join(rootURL, "DatabaseSplitted.csv")

# global variables
shutterSpeed = 1 # the time between 2 imageGrabs

