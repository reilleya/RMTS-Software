import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal

from ui.views.MainWindow_ui import Ui_MainWindow
from lib.radio import setupPacket, firePacket, resultPacket

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.ui.tabStart.beginSetup.connect(self.beginSetup)
        self.ui.tabStart.recvResults.connect(self.recvResults)
        self.ui.tabSetup.beginFire.connect(self.beginFire)

    def closeEvent(self, event=None):
        self.closed.emit()
        sys.exit()

    def routePacket(self, packet):
        if type(packet) is setupPacket:
            self.ui.tabSetup.processSetupPacket(packet)
        if type(packet) is resultPacket:
            self.ui.tabResults.processResultsPacket(packet)

    def beginSetup(self, port, converter):
        self.app.rm.run(port)
        self.ui.tabSetup.setConverter(converter)
        self.ui.tabWidget.setCurrentIndex(1)

    def beginFire(self, firingConfig, converter):
        self.ui.tabResults.newFire(converter)
        recordingDur = int(firingConfig['recordingDuration'] * 1000)
        firingDur = int(firingConfig['firingDuration'] * 1000)
        firePack = firePacket(recordingDur, firingDur)
        self.app.rm.sendPacket(firePack)
        self.ui.tabWidget.setCurrentIndex(2)

    def recvResults(self, port, converter):
        self.app.rm.run(port)
        self.ui.tabResults.newFire(converter)
        self.ui.tabWidget.setCurrentIndex(2)
