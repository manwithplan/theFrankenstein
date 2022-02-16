import win32gui
from typing import List, Set, Dict, Tuple, Optional, Union, Any, TypeVar, Bytes
import logging


class screenDetection:
    """
    This class is responsible for finding the activation status of the game window.
    It does it by getting a list of all open windows and checking if the name of the game screen
    matches one of the names.

    ...

    Attributes
    ----------
    screenName : str
        (Part of the) name of the window we are trying to detect

    screenOpen : bool
        Flag for the detection status of the game window

    screenCoordinates : List of ints
        List containing the coordinate of the screen we need.

    Methods
    -------

    getImage() :
        returns the current image

    """

    def __init__(self, screenName: str = "Elite - Dangerous (CLIENT)") -> None:
        super().__init__()

        # initalize logger object
        self.logger: object = logging.getLogger(__name__)
        self.logger.info("screenDetection object initialized")

        self.screenOpen: bool = False
        self.screenCoordinates: List[int] = []
        self.screenName: str = screenName

    def checkGameActive(self) -> None:
        """
        The second part of this function calls the enumerator on the open windows, and first
        gives the logic to search for the game window.
        """

        def enumerationHandler(hwnd, ctx):
            # this function defines the functionality of what to do for each open window.
            if win32gui.IsWindowVisible(hwnd):
                if self.screenName in win32gui.GetWindowText(hwnd):
                    self.screenOpen = True
                    self.logger.info(f"game window found method called and visible")

        win32gui.EnumWindows(enumerationHandler, None)

    def getScreenCoordinates(self) -> List[int]:
        """
        Method that finds the coordinates of the game window once it has been found.
        """
        if self.screenOpen:
            hwnd: List[int] = win32gui.FindWindow(None, self.screenName)
            self.screenCoordinates: List[int] = win32gui.GetWindowRect(hwnd)

            self.logger.info(f"game window found with coordinates {hwnd}")

            return self.screenCoordinates

        return None
