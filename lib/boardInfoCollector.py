from PyQt5.QtCore import QObject, pyqtSignal

from .radio import RadioManager, SetupPacket, ErrorPacket, VersionPacket
from .logger import logger
from .errors import formatErrorMessage

class BoardInfoCollector(QObject):
    resetDataAge = pyqtSignal()
    error = pyqtSignal(list)
    version = pyqtSignal(dict)
    disconnected = pyqtSignal()

    def __init__(self, port):
        super().__init__()
        self.port = port

        self.radioManager = RadioManager()
        self.radioManager.newPacket.connect(self.newPacket)

        self.errors = None
        self.versionInfo = None

    def connect(self):
        self.radioManager.run(self.port)

    def newPacket(self, packet):
        self.resetDataAge.emit()
        if type(packet) is SetupPacket:
            errors = [0 for device in range(3)]
            self.checkErrors(errors)
        elif type(packet) is ErrorPacket:
            self.checkErrors(packet.getErrorList())
        elif type(packet) is VersionPacket:
            if self.versionInfo is None:
                logger.log('Got version info ({})'.format(packet))
                self.versionInfo = {
                    'hardware': packet.hardwareVersion,
                    'firmware': packet.firmwareVersion
                }
                self.version.emit(self.versionInfo)

    def checkErrors(self, errorList):
        if errorList != self.errors:
            logger.log('New error list: ({})'.format(errorList))
            self.errors = errorList
            self.error.emit([formatErrorMessage(i, err) for i, err in enumerate(errorList)])

    def exit(self):
        self.radioManager.stop()
        self.disconnected.emit()
