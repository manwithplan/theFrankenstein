from typing import List, Set, Dict, Tuple, Optional, Union, Any
import logging

from Settings.Settings import rootURL

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QMainWindow
from PySide6.QtCore import (
    QFile,
    QIODevice,
    QObject,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
)
from PySide6.QtGui import QIcon, QPixmap, QMovie

class guiMain:
    """
    A class to create and present a GUI.

    ...

    Attributes
    ----------
    gui : obj
        object containg gui
    logger : str
        class specific GUI

    Classes
    -------
    guiMain
        controls the sequencing of the screens.
    login
        contains the first login screen for e-mail and password
    loginSplash
        contains the loading screen during authentication
    homeScreen
        Main GUI screen containing all sub-menu's and data.

    Methods
    -------
    setExternalFunctions(function):
        Allows for using external functions as triggers in the GUI

    openLogin():
        callback function for loading the login window

    openLoginSplash():
        callback function for loading the splash window

    openMain():
        callback function for loading the main window

    """

    def __init__(self) -> None:
        super().__init__()
        self.gui: object = None
        self.logger: object = logging.getLogger(__name__)

    def setExternalFunctions(self, detectGameWindow) -> None:
        """
        Loading an external function to detect Game Window into the GUI functionality
        """
        self.detectGameWindow: object = detectGameWindow

    def openLogin(self) -> None:
        """
        Loads Login screen
        """
        self.gui = self.login(self.openLoginSplash)

    def openLoginSplash(self) -> None:
        """
        Loads Login Splash screen
        """
        self.gui = self.loginSplash(self.openMain)

    def openMain(self) -> None:
        """
        Loads Main Screen
        """
        self.gui = self.homeScreen(self.detectGameWindow)

    class login(QObject):
        """
        GUI element for the login screen. Inherits from GObject class

        ...

        Attributes
        ----------
        name : obj
            placeholder for user name input
        password : str
            placeholder for user password input
        btn : PyQT obj
            button on the GUI screen

        Methods
        -------
        connectHandler():
            Function that gets called when clicking "login" button.

        """

        def __init__(
            self,
            nextWindow,
            ui_file=rootURL + r"\theGUI\ui\LogInScreen.ui",
            parent=None,
        ) -> None:
            super(self.login, self).__init__(parent)

            self.nextWindow: object = nextWindow

            ui_file: object = QFile(ui_file)
            ui_file.open(QFile.ReadOnly)

            loader: object = QUiLoader()
            self.login: object = loader.load(ui_file)
            ui_file.close()

            self.name: object = self.login.findChild(QLineEdit, "line_Name")
            self.password: object = self.login.findChild(QLineEdit, "line_Password")

            btn: object = self.login.findChild(QPushButton, "button_SignIn")
            btn.clicked.connect(self.connectHandler)
            self.login.show()

            self.logger.info("login window activated")

        def connectHandler(self) -> None:
            """
            Function that gets called when login button is called. It gathers the user
            inputted name and password and pretends to login.
            """
            name: object = "None" if not self.name.text() else self.name.text()
            password: object = (
                "None" if not self.password.text() else self.password.text()
            )

            self.logger.info("login attempt for name: {name} and password:  {password}")

            self.login.close()
            self.nextWindow()

    class loginSplash(QObject):
        """
        GUI element for the login Splash screen. Inherits from GObject class.
        It shows a loading icon and pretends to communicate with the server.

        ...

        Attributes
        ----------
        loader : PyQT obj
            Custom PyQT loader object
        timer : PyQT str
            timer keeps track of progress

        Methods
        -------
        progress():
            Function that increments the counter variable.

        progressBarValue():
            Function that creates the login icon and increments it.

        """

        def __init__(
            self,
            nextWindow,
            ui_file=rootURL + r"\theGUI\ui\LogInSplash.ui",
            parent=None,
        ) -> None:
            super(self.loginSplash, self).__init__(parent)

            self.nextWindow = nextWindow

            ui_file = QFile(ui_file)
            ui_file.open(QFile.ReadOnly)

            loader = QUiLoader()
            self.loginSplash = loader.load(ui_file)
            ui_file.close()

            self.progressBarValue(0)

            ## QTIMER ==> START
            self.timer: object = QTimer()
            self.timer.timeout.connect(self.progress)
            # TIMER IN MILLISECONDS
            self.timer.start(35)

            self.loginSplash.show()

        def progress(self) -> None:
            """
            Keeps track of the counter variable that increments to 100, and communicates
            this value with the progress bar method..
            """

            # SET VALUE TO PROGRESS BAR
            self.progressBarValue(self.counter)

            # CLOSE SPLASH SCREE AND OPEN APP
            if self.counter > 100:
                # STOP TIMER
                self.timer.stop()

                # SHOW MAIN WINDOW
                # self.main = MainWindow()
                # self.main.show()

                # CLOSE SPLASH SCREEN
                self.loginSplash.close()
                self.nextWindow()

            # INCREASE COUNTER
            self.counter += 2

        def progressBarValue(self, value) -> None:
            """
            function that updates the Counter value with the progress bar.

            :value: int representing progress
            """

            styleSheet = """
            QFrame{
                border-radius: 75px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(0, 0, 0, 0), stop:{STOP_2} rgba(81, 183, 187, 255));
            }
            """

            progress: float = (100 - value) / 100.0

            stop_1 = str(progress - 0.001)
            stop_2 = str(progress)

            newStyleSheet = styleSheet.replace("{STOP_1}", stop_1).replace(
                "{STOP_2}", stop_2
            )

            self.loginSplash.circularProgress.setStyleSheet(newStyleSheet)

    class homeScreen(QObject):
        """
        GUI element for the main screen. Inherits from GObject class.
        allow navigation between user, settings and main menu
        and features status updates of the app.

        ...

        Attributes
        ----------
        btn : PyQT obj
            button for togging menu on and off
        homescreen : PyQT obj
            placeholder for the differen sub-menu's of the GUI

        Methods
        -------
        toggleHandler():
            Function that shows or hides the sidebar when it is clicked.

        """

        def __init__(
            self,
            detectGameWindow: object,
            ui_file: str = rootURL + r"\theGUI\ui\HomeScreen.ui",
            parent=None,
        ) -> None:
            super(self.homeScreen, self).__init__(parent)
            ui_file: object = QFile(ui_file)
            ui_file.open(QFile.ReadOnly)

            loader: object = QUiLoader()
            self.homeScreen: object = loader.load(ui_file)
            ui_file.close()

            ### initialize all external methods
            self.detectGameWindow = detectGameWindow

            ### initialize all media

            # mainPage buttons
            self.homeScreen.toggleButton.setIcon(
                QIcon(rootURL + r"\theGUI\resources\icons\cil-menu.png")
            )

            # accountPage buttons
            self.homeScreen.userImage.setPixmap(
                QPixmap(rootURL + r"\theGUI\resources\icons\cil-user.png")
            )
            self.homeScreen.statusCheck.setPixmap(
                QPixmap(rootURL + r"\theGUI\resources\icons\cil-check-circle.png")
            )
            self.homeScreen.gameIcon.setPixmap(
                QPixmap(rootURL + r"\theGUI\resources\icons\cil-gamePad.png")
            )
            self.homeScreen.game1Image.setPixmap(
                QPixmap(rootURL + r"\theGUI\resources\icons\elite-dangerous.png")
            )

            # load activeIcon to frame
            iconActive = QPixmap(rootURL + r"\theGUI\resources\icons\activeLit.png")
            self.homeScreen.labelActive0.setPixmap(iconActive)
            self.homeScreen.labelActive0.setScaledContents(True)

            # set up buttons
            btn = self.homeScreen.findChild(QPushButton, "toggleButton")
            btn.clicked.connect(lambda: self.toggleHandler(50, True))

            # set up pages and corresponding button
            self.homeScreen.homePages.setCurrentWidget(self.homeScreen.homePage)

            self.homeScreen.btnMain.clicked.connect(
                lambda: self.homeScreen.homePages.setCurrentWidget(
                    self.homeScreen.homePage
                )
            )
            self.homeScreen.btnAccount.clicked.connect(
                lambda: self.homeScreen.homePages.setCurrentWidget(
                    self.homeScreen.accountPage
                )
            )
            self.homeScreen.btnSettings.clicked.connect(
                lambda: self.homeScreen.homePages.setCurrentWidget(
                    self.homeScreen.settingsPage
                )
            )

            ### show the screen
            self.homeScreen.show()

        def toggleHandler(self, maxWidth: int, enable: bool) -> None:
            """
            Functions that controls the extension of the sidebar's menu and icons.

            :maxWidth: int representing width of the sidebar
            :enable: boolean flag representing opened or closed state.
            """

            def showIcon():
                """
                function for extending the sidebar menu
                """

                if widthExtended == maxExtend:

                    # make pushbutton icons appear when folding menu out.
                    self.homeScreen.btnMain.setIcon(
                        QIcon(rootURL + r"\theGUI\resources\icons\cil-home.png")
                    )
                    self.homeScreen.btnAccount.setIcon(
                        QIcon(rootURL + r"\theGUI\resources\icons\cil-user.png")
                    )
                    self.homeScreen.btnSettings.setIcon(
                        QIcon(rootURL + r"\theGUI\resources\icons\cil-settings.png")
                    )

            def hideIcon():
                """
                Function for inclining the sidebar menu
                """

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
                self.animation: object = QPropertyAnimation(
                    self.homeScreen.menuBtnBar, b"minimumWidth"
                )
                self.animation.setDuration(400)
                self.animation.setStartValue(barWidth)
                self.animation.setEndValue(widthExtended)
                self.animation.setEasingCurve(QEasingCurve.InOutQuart)
                self.animation.start()

                self.animation.finished.connect(lambda: showIcon())
