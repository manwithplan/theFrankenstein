from threading import Thread
import time


class getInput(Thread):
    """
    Basic UI that runs in terminal and allow user to control music by selecting inputs with keyboard.

    ...

    Attributes
    ----------
    userInput : str
        input gathered from user

    Methods
    -------
    run() :
        function that gets called when running in thread. reads user input from terminal.

    clearInput():
        clears input.

    """

    def __init__(self):
        Thread.__init__(self)
        self.stopFlag = False
        self.userInput = ""
        self.start()

    def run(self):
        while not self.stopFlag:
            self.userInput = input("Enter command here : ")

    def clearInput(self):
        self.userInput = ""
