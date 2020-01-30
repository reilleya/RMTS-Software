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
        t = []
        f = []
        p = []

        recv = list(self.rawData.keys())
        recv.sort()
        for i in recv:
            t.append(self.rawData[i].time)
            f.append(self.rawData[i].force)
            p.append(self.rawData[i].pressure)

        raw = {'time':t[:], 'force':f[:], 'pressure':p[:]}

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
        recordingDur = int(self.motorInfo.getProperty('recordingDuration') * 1000)
        firingDur = int(self.motorInfo.getProperty('firingDuration') * 1000)
        firePack = FirePacket(recordingDur, firingDur)
        self.radioManager.sendPacket(firePack)
        self.fired.emit()

    def stop(self):
        stopPack = StopPacket()
        self.radioManager.sendPacket(stopPack)
        self.stopped.emit()

    def exit(self):
        self.radioManager.stop()

    # Todo: Outdated:
    def toDictionary(self):
        out = {
            'rawData': {i: {'t': v.time, 'f': v.force, 'p':v.pressure} for i, v in self.rawData.items()},
            'motorInfo': self.motorInfo.getProperties(),
            'converter': self.converter.toDictionary()
        }
        return out

    def fromDictionary(self, data):
        self.converter = Converter.fromDictionary(data['converter'])
        self.motorInfo = MotorConfig()
        self.motorInfo.setProperties(data['motorInfo'])
        self.rawData = {}
        for index, element in data['rawData'].items():
            packet = ResultPacket(None) # Todo: don't use packets for this
            packet.time = element['t']
            packet.force = element['f']
            packet.pressure = element['p']
            self.rawData[index] = packet
        self.newGraph.emit(self.processRawData())
