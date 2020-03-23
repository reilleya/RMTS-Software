from PyQt5.QtCore import QObject, pyqtSignal

from .converter import Converter
from .radio import RadioManager, SetupPacket, FirePacket, ResultPacket, ErrorPacket, StopPacket
from .motor import processRawData

PACKET_STRIDE = 10

class Firing(QObject):
    newGraph = pyqtSignal(object)
    newSetupPacket = pyqtSignal(object)
    newErrorPacket = pyqtSignal(object)

    fired = pyqtSignal()
    stopped = pyqtSignal()
    hasResults = pyqtSignal()

    def __init__(self, forceConverter, pressureConverter, motorInfo, port):
        super().__init__()
        self.rawData = {}
        self.startIndex = None
        self.lastSend = 0

        self.forceConverter = forceConverter
        self.pressureConverter = pressureConverter
        self.motorInfo = motorInfo

        self.radioManager = RadioManager()
        self.radioManager.newPacket.connect(self.newPacket)
        self.radioManager.run(port)

    def processRawData(self):
        raw = {'time': [], 'force': [], 'pressure': []}

        recv = list(self.rawData.keys())
        recv.sort()
        for i in recv:
            raw['time'].append(self.rawData[i].time)
            raw['force'].append(self.rawData[i].force)
            raw['pressure'].append(self.rawData[i].pressure)

        return processRawData(raw, self.forceConverter, self.pressureConverter, self.motorInfo)

    def newPacket(self, packet):
        if type(packet) is SetupPacket:
            self.newSetupPacket.emit(packet)
        elif type(packet) is ErrorPacket:
            self.newErrorPacket.emit(packet)
        elif type(packet) is ResultPacket:
            self.rawData[packet.seqNum] = packet
            if len(self.rawData) == 1:
                self.startIndex = packet.seqNum
            elif abs(packet.seqNum - self.startIndex) < PACKET_STRIDE:
                if len(self.rawData) > self.lastSend and self.motorInfo is not None:
                    res = self.processRawData()
                    self.lastSend = len(self.rawData)
                    self.newGraph.emit(res)

    def fire(self):
        firingDur = int(self.motorInfo.getProperty('firingDuration') * 1000)
        firePack = FirePacket(firingDur)
        self.radioManager.sendPacket(firePack)
        self.fired.emit()

    def stop(self):
        stopPack = StopPacket()
        self.radioManager.sendPacket(stopPack)
        self.stopped.emit()

    def exit(self):
        self.radioManager.stop()
