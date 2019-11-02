import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal

from ui.views.MainWindow_ui import Ui_MainWindow
from lib.radio import setupPacket

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.ui.tabStart.beginSetup.connect(self.beginSetup)
        self.ui.tabSetup.beginFire.connect(self.beginFire)

    def closeEvent(self, event=None):
        self.closed.emit()
        sys.exit()

    def routePacket(self, packet):
        if type(packet) is setupPacket:
            self.ui.tabSetup.processSetupPacket(packet)

    def beginSetup(self, port):
        self.app.rm.run(port)
        self.ui.tabWidget.setCurrentIndex(1)

    def beginFire(self, firingConfig):
        print(firingConfig)
        #self.app.rm
        self.ui.tabWidget.setCurrentIndex(2)
