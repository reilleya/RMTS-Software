import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal

from ui.views.MainWindow_ui import Ui_MainWindow
from lib.radio import SetupPacket, FirePacket, ResultPacket, StopPacket

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.ui.tabStart.beginSetup.connect(self.beginSetup)
        self.ui.tabStart.recvResults.connect(self.recvResults)

        self.ui.tabSetup.gotoFirePage.connect(self.gotoFirePage)
        self.ui.tabSetup.newFiringConfig.connect(self.app.setFiringConfig)

        self.ui.tabFire.setup.connect(self.gotoSetupPage)
        self.ui.tabFire.results.connect(self.gotoResultsPage)
        self.ui.tabFire.fire.connect(self.sendFire)
        self.ui.tabFire.stop.connect(self.sendStop)

    def closeEvent(self, event=None):
        self.closed.emit()
        sys.exit()

    def routePacket(self, packet):
        if type(packet) is SetupPacket:
            self.ui.tabSetup.processSetupPacket(packet)
        if type(packet) is ResultPacket:
            self.ui.tabResults.processResultsPacket(packet)

    def gotoSetupPage(self):
        self.ui.tabSetup.setup()
        self.ui.tabWidget.setCurrentIndex(1)

    def gotoFirePage(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def gotoResultsPage(self):
        self.ui.tabWidget.setCurrentIndex(3)


    def beginSetup(self, port, converter):
        self.app.rm.run(port)
        self.app.setConverter(converter)
        self.gotoSetupPage()

    def recvResults(self, port, converter):
        self.app.rm.run(port)
        self.app.setConverter(converter)
        self.ui.tabResults.newFire()
        self.gotoResultsPage()


    def sendFire(self):
        firingConfig = self.app.getFiringConfig()
        self.ui.tabResults.newFire()
        recordingDur = int(firingConfig['recordingDuration'] * 1000)
        firingDur = int(firingConfig['firingDuration'] * 1000)
        firePack = FirePacket(recordingDur, firingDur)
        self.app.rm.sendPacket(firePack)

    def sendStop(self):
        stopPack = StopPacket()
        self.app.rm.sendPacket(stopPack)
