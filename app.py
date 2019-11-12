import sys

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal

from lib.radio import RadioManager
from ui.mainWindow import MainWindow

class App(QApplication):

    newConverter = pyqtSignal(object)
    newFiringConfig = pyqtSignal(object)

    def __init__(self, args):
        super().__init__(args)
        self.rm = RadioManager()

        self.converter = None
        self.firingConfig = None

        self.window = MainWindow(self)
        self.rm.newPacket.connect(self.window.routePacket)
        self.window.closed.connect(self.rm.stop)
        self.window.show()


    def outputMessage(self, content, title='RMTSI'):
        msg = QMessageBox()
        msg.setText(content)
        msg.setWindowTitle(title)
        msg.exec_()

    def outputException(self, exception, text, title='RMTSI - Error'):
        msg = QMessageBox()
        msg.setText(text)
        msg.setInformativeText(str(exception))
        msg.setWindowTitle(title)
        msg.exec_()

    def setConverter(self, converter):
        self.converter = converter
        self.newConverter.emit(converter)

    def getConverter(self):
        return self.converter

    def setFiringConfig(self, firingConfig):
        self.firingConfig = firingConfig
        self.newFiringConfig.emit(firingConfig)

    def getFiringConfig(self):
        return self.firingConfig
