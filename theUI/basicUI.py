from threading import Thread
import time

class getInput(Thread):
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