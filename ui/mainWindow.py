import sys
from enum import IntEnum
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal

from ui.views.MainWindow_ui import Ui_MainWindow
from lib.radio import SetupPacket, FirePacket, ResultPacket, StopPacket, CalStartPacket, CalStopPacket
from lib.firing import Firing

class MainWindowPages(IntEnum):
    START = 0
    RECV_MOTOR_DATA = 1
    SETUP_FIRE = 2
    RESULTS = 3
    PREFERENCES = 4
    CALIBRATE = 5

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.ui.pageStart.beginSetup.connect(self.gotoSetupPage)
        self.ui.pageStart.recvResults.connect(self.recvResults)
        self.ui.pageStart.editPreferences.connect(self.gotoPreferencesPage)
        self.ui.pageStart.calibrate.connect(self.gotoCalibratePage)
        self.ui.pageStart.showFireFile.connect(self.showLoadedFiring)

        self.ui.pageRecvMotorData.nextPage.connect(self.recvResultsMotorDataSet)

        self.ui.pageFire.results.connect(self.gotoResultsPage)

        self.ui.pageResults.back.connect(self.gotoStartPage)

        self.ui.pagePreferences.back.connect(self.gotoStartPage)

        self.ui.pageCalibrate.back.connect(self.gotoStartPage)

        self.firingConfig = None
        self.firing = None

    def closeEvent(self, event=None):
        self.closed.emit()
        self.ui.pageFire.exit()
        self.ui.pageCalibrate.exit()
        sys.exit()

    def gotoPage(self, page):
        self.ui.stackedWidget.setCurrentIndex(int(page))

    def gotoStartPage(self):
        self.gotoPage(MainWindowPages.START)

    def gotoSetupPage(self):
        self.gotoPage(MainWindowPages.SETUP_FIRE)

    def gotoRecvMotorDataPage(self):
        self.ui.pageRecvMotorData.setup()
        self.gotoPage(MainWindowPages.RECV_MOTOR_DATA)

    def gotoResultsPage(self):
        self.gotoPage(MainWindowPages.RESULTS)

    def gotoCalibratePage(self):
        self.gotoPage(MainWindowPages.CALIBRATE)

    def gotoPreferencesPage(self):
        self.ui.pagePreferences.setup()
        self.gotoPage(MainWindowPages.PREFERENCES)

    def newFiringConfig(self, config):
        self.firingConfig = config
        self.firing.setMotorInfo(config.getMotorInfo())

    def recvResults(self, port, converter):
        self.app.rm.run(port)
        self.firing = Firing(converter)
        self.gotoRecvMotorDataPage()

    def recvResultsMotorDataSet(self, motorData):
        self.firing.setMotorInfo(motorData)
        self.ui.pageResults.setFiring(self.firing)
        self.gotoResultsPage()

    def showLoadedFiring(self, data):
        self.firing = Firing()
        self.ui.pageResults.setFiring(self.firing)
        self.firing.fromDictionary(data)
        self.gotoResultsPage()
