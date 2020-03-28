from PyQt5.QtCore import QObject, pyqtSignal

from .radio import RadioManager, SetupPacket
from .filter import LowPass

class Calibration(QObject):
    newLoadCellReading = pyqtSignal(float)
    newPressureTransducerReading = pyqtSignal(object)
    resetDataAge = pyqtSignal()

    def __init__(self, port):
        super().__init__()
        self.loadCellFilter = LowPass(25)
        self.pressureTransducerFilter = LowPass(25)

        self.radioManager = RadioManager()
        self.radioManager.newPacket.connect(self.newPacket)
        self.radioManager.run(port)

    def newPacket(self, packet):
        self.resetDataAge.emit()
        if type(packet) is SetupPacket:
            self.newLoadCellReading.emit(self.loadCellFilter.addData(packet.force))
            self.newPressureTransducerReading.emit(self.pressureTransducerFilter.addData(packet.pressure))

    def exit(self):
        self.radioManager.stop()
