from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from lib.logger import logger

class ErrorCollector(QObject):
    newError = pyqtSignal()
    hasError = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.errors = []

    def recordError(self, packet):
        newError = False
        for error in packet.getErrors():
            if error not in self.errors:
                self.errors.append(error)
                newError = True
        if newError:
            logger.log('Got an error packet with details ({})'.format(packet))
            output = "The RMTS board reported the following error(s):\n\n"
            output += "\n".join(self.errors)
            output += "\n\n Please resolve them and restart the device before continuing."
            QApplication.instance().outputMessage(output)
            self.newError.emit()
        if len(self.errors) > 0:
            self.hasError.emit()
