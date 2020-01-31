from PyQt5.QtCore import QObject, pyqtSignal

from .converter import Converter
from .radio import RadioManager, SetupPacket, FirePacket, ResultPacket, ErrorPacket, StopPacket
from .filter import LowPass

PACKET_STRIDE = 10

class Calibration(QObject):
    newLoadCellReading = pyqtSignal(float)
    newPressureTransducerReading = pyqtSignal(object)

    def __init__(self, port):
        super().__init__()
        self.loadCellFilter = LowPass(25)
        self.pressureTransducerFilter = LowPass(25)

        self.radioManager = RadioManager()
        self.radioManager.newPacket.connect(self.newPacket)
        self.radioManager.run(port)

    def newPacket(self, packet):
        if type(packet) is SetupPacket:
            self.newLoadCellReading.emit(self.loadCellFilter.addData(packet.force))
            self.newPressureTransducerReading.emit(self.pressureTransducerFilter.addData(packet.pressure))

    def exit(self):
        self.radioManager.stop()
