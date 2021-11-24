"""

this class contains the GUI.
- : guiMain controls the sequence of screens.
1: login contains the code for the first screen of the UI
2: loginSplash containg code for the loading screen
3: homeScreen contains the main screen, all the pages in the stackedWidget and implements the UI functionality of all the other implemented method.

"""

import sys
import time
import threading

from Settings.Settings import rootURL

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QMainWindow
from PySide6.QtCore import QFile, QIODevice, QObject, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QIcon, QPixmap, QMovie

## ==> GLOBALS
counter = 0

class guiMain():
    def __init__(self):
        super().__init__()
        self.gui = None

    def setExternalFunctions(self, detectGameWindow):
        self.detectGameWindow = detectGameWindow

    def openLogin(self):
        self.gui = login(self.openLoginSplash)

    def openLoginSplash(self):
        self.gui = loginSplash(self.openMain)

    def openMain(self):
        self.gui = homeScreen(self.detectGameWindow)

class login(QObject):

    def __init__(self, nextWindow, ui_file = rootURL + r"\theGUI\ui\LogInScreen.ui", parent=None):
        super(login, self).__init__(parent)

        self.nextWindow = nextWindow

        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.login = loader.load(ui_file)
        ui_file.close()
        
        self.name = self.login.findChild(QLineEdit, 'line_Name')
        self.password = self.login.findChild(QLineEdit, 'line_Password')
        
        btn = self.login.findChild(QPushButton, 'button_SignIn')
        btn.clicked.connect(self.connectHandler)
        self.login.show()

    def connectHandler(self):
        name = 'None' if not self.name.text() else self.name.text()
        password = 'None' if not self.password.text() else self.password.text()

        #print('login: {} - {}'.format(name, password))

        self.login.close()
        self.nextWindow()

class loginSplash(QObject):

    def __init__(self, nextWindow, ui_file = rootURL + r"\theGUI\ui\LogInSplash.ui", parent=None):
        super(loginSplash, self).__init__(parent)

        self.nextWindow = nextWindow

        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.loginSplash = loader.load(ui_file)
        ui_file.close()

        self.progressBarValue(0)

        ## QTIMER ==> START
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)
        
        self.loginSplash.show()

    def progress(self):

        global counter

        # SET VALUE TO PROGRESS BAR
        self.progressBarValue(counter)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            #self.main = MainWindow()
            #self.main.show()

            # CLOSE SPLASH SCREEN
            self.loginSplash.close()
            self.nextWindow()

        # INCREASE COUNTER
        counter += 2

    def progressBarValue(self, value):

        styleSheet = """
        QFrame{
            border-radius: 75px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(0, 0, 0, 0), stop:{STOP_2} rgba(81, 183, 187, 255));
        }
        """

        progress = (100 - value) / 100.0

        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        newStyleSheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

        self.loginSplash.circularProgress.setStyleSheet(newStyleSheet)

class homeScreen(QObject):

    def __init__(self,  detectGameWindow, ui_file = rootURL + r"\theGUI\ui\HomeScreen.ui", parent=None):
        super(homeScreen, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.homeScreen = loader.load(ui_file)
        ui_file.close()

        ### initialize all external methods
        self.detectGameWindow = detectGameWindow
        
        ### initialize all media

        # mainPage buttons
        self.homeScreen.toggleButton.setIcon(QIcon(rootURL + r"\theGUI\resources\icons\cil-menu.png"))

        # accountPage buttons
        self.homeScreen.userImage.setPixmap(QPixmap(rootURL + r"\theGUI\resources\icons\cil-user.png"))
        self.homeScreen.statusCheck.setPixmap(QPixmap(rootURL + r"\theGUI\resources\icons\cil-check-circle.png"))
        self.homeScreen.gameIcon.setPixmap(QPixmap(rootURL + r"\theGUI\resources\icons\cil-gamePad.png"))
        self.homeScreen.game1Image.setPixmap(QPixmap(rootURL + r"\theGUI\resources\icons\elite-dangerous.png"))

        # load activeIcon to frame
        iconActive = QPixmap(rootURL + r"\theGUI\resources\icons\activeLit.png")
        self.homeScreen.labelActive0.setPixmap(iconActive)
        self.homeScreen.labelActive0.setScaledContents(True)
       
        # set up buttons
        btn = self.homeScreen.findChild(QPushButton, 'toggleButton')
        btn.clicked.connect(lambda: self.toggleHandler(50, True))

        # set up pages and corresponding button
        self.homeScreen.homePages.setCurrentWidget(self.homeScreen.homePage)

        self.homeScreen.btnMain.clicked.connect(lambda: self.homeScreen.homePages.setCurrentWidget(self.homeScreen.homePage))
        self.homeScreen.btnAccount.clicked.connect(lambda: self.homeScreen.homePages.setCurrentWidget(self.homeScreen.accountPage))
        self.homeScreen.btnSettings.clicked.connect(lambda: self.homeScreen.homePages.setCurrentWidget(self.homeScreen.settingsPage))

        ### show the screen
        self.homeScreen.show()

    def toggleHandler(self, maxWidth, enable):
        def showIcon():

            if widthExtended == maxExtend:

                # make pushbutton icons appear when folding menu out.
                self.homeScreen.btnMain.setIcon(QIcon(rootURL + r"\theGUI\resources\icons\cil-home.png"))
                self.homeScreen.btnAccount.setIcon(QIcon(rootURL + r"\theGUI\resources\icons\cil-user.png"))
                self.homeScreen.btnSettings.setIcon(QIcon(rootURL + r"\theGUI\resources\icons\cil-settings.png"))
        
        def hideIcon():

            if widthExtended == barStandardWidth:
                # make the pushbutton dissapeasr when folding in
                self.homeScreen.btnMain.setIcon(QIcon(QPixmap()))
                self.homeScreen.btnAccount.setIcon(QIcon(QPixmap()))
                self.homeScreen.btnSettings.setIcon(QIcon(QPixmap()))

        if enable: 

            # get width
            barWidth = self.homeScreen.menuBtnBar.width()
            maxExtend = maxWidth
            barStandardWidth = 10

            # set max width
            if barWidth == barStandardWidth:
                widthExtended = maxExtend

            else:
                widthExtended = barStandardWidth
                hideIcon()

            # animation of the menubar size.
            self.animation = QPropertyAnimation(self.homeScreen.menuBtnBar, b"minimumWidth")
            self.animation.setDuration(400)
            self.animation.setStartValue(barWidth)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()
            
            self.animation.finished.connect(lambda: showIcon())


