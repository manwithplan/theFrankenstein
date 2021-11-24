"""

This class is responsible for tracking down the activation and status of the game window. 
It does it by getting a list of all open windows and checking if the name of the game screen 
matches one of the names.

"""

# temporary imports
import win32gui

class screenDetection():
    def __init__(self):
        super().__init__()
        self.screenOpen = False
        self.screenCoordinates = []

    def checkGameActive(self):
        # the second part of this function calls the enumerator on the open windows, and first 
        # gives the function to run on each one.

        def enumerationHandler(hwnd, ctx):
            # this function defines the functionality of what to do for each open window.
            if win32gui.IsWindowVisible( hwnd ):
                if "Elite - Dangerous (CLIENT)" in win32gui.GetWindowText( hwnd ):
                    self.screenOpen = True
            
        win32gui.EnumWindows( enumerationHandler, None )

    def getScreenCoordinates(self):
        if self.screenOpen:
            hwnd = win32gui.FindWindow(None, "Elite - Dangerous (CLIENT)")
            self.screenCoordinates = win32gui.GetWindowRect(hwnd)
            
            return self.screenCoordinates

        return None
