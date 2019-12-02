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
    FIRING_SETUP = 2
    FIRE = 3
    RESULTS = 4
    PREFERENCES = 5

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.ui.pageStart.beginSetup.connect(self.beginSetup)
        self.ui.pageStart.recvResults.connect(self.recvResults)
        self.ui.pageStart.editPreferences.connect(self.gotoPreferencesPage)

        self.ui.pageSetup.gotoFirePage.connect(self.gotoFirePage)
        self.ui.pageRecvMotorData.nextPage.connect(self.recvResultsMotorDataSet)
        self.ui.pageSetup.newFiringConfig.connect(self.newFiringConfig)
        self.ui.pageSetup.calibrate.connect(self.app.rm.runCalibration)

        self.ui.pageFire.setup.connect(self.gotoSetupPage)
        self.ui.pageFire.results.connect(self.gotoResultsPage)
        self.ui.pageFire.fire.connect(self.sendFire)
        self.ui.pageFire.stop.connect(self.sendStop)

        self.ui.pagePreferences.back.connect(self.gotoStartPage)

        self.firingConfig = None
        self.firing = None

    def closeEvent(self, event=None):
        self.closed.emit()
        sys.exit()

    def routePacket(self, packet):
        if type(packet) is SetupPacket:
            self.ui.pageSetup.processSetupPacket(packet)
        if type(packet) is ResultPacket:
            if self.firing is not None:
                self.firing.addDatapoint(packet)
            else:
                print('Got results packet without a firing to add it to')

    def gotoPage(self, page):
        self.ui.stackedWidget.setCurrentIndex(int(page))

    def gotoStartPage(self):
        self.gotoPage(MainWindowPages.START)

    def gotoSetupPage(self):
        self.gotoPage(MainWindowPages.FIRING_SETUP)

    def gotoFirePage(self):
        self.gotoPage(MainWindowPages.FIRE)

    def gotoRecvMotorDataPage(self):
        self.gotoPage(MainWindowPages.RECV_MOTOR_DATA)

    def gotoResultsPage(self):
        self.gotoPage(MainWindowPages.RESULTS)

    def gotoPreferencesPage(self):
        self.ui.pagePreferences.setup()
        self.gotoPage(MainWindowPages.PREFERENCES)


    def beginSetup(self, port, converter):
        self.app.rm.run(port)
        self.ui.pageSetup.setup(converter)
        self.firing = Firing(converter)
        self.ui.pageResults.setFiring(self.firing)
        self.gotoSetupPage()

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

    def sendFire(self):
        recordingDur = int(self.firingConfig.getProperty('recordingDuration') * 1000)
        firingDur = int(self.firingConfig.getProperty('firingDuration') * 1000)
        firePack = FirePacket(recordingDur, firingDur)
        self.app.rm.sendPacket(firePack)

    def sendStop(self):
        stopPack = StopPacket()
        self.app.rm.sendPacket(stopPack)
