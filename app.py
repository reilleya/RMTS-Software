import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from lib.radio import RadioManager
from ui.mainWindow import MainWindow

class App(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.rm = RadioManager()

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
