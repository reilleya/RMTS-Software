from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal

from .converter import Converter
from .radio import RadioManager, SetupPacket, FirePacket, ResultPacket, ErrorPacket, StopPacket, VersionPacket
from .motor import processRawData
from .firmwareVersions import checkVersionPacket

PACKET_STRIDE = 10

class VERSION_CHECK_STATE(Enum):
    UNCHECKED = 1
    SUCCESS = 2
    FAILURE = 3


class Firing(QObject):
    newGraph = pyqtSignal(object)
    newSetupPacket = pyqtSignal(object)
    newErrorPacket = pyqtSignal(object)

    fired = pyqtSignal()
    stopped = pyqtSignal()
    hasResults = pyqtSignal()

    def __init__(self, forceConverter, pressureConverter, motorInfo, port):
        super().__init__()
        self.versionChecked = VERSION_CHECK_STATE.UNCHECKED

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
        if type(packet) is VersionPacket and self.versionChecked == VERSION_CHECK_STATE.UNCHECKED:
            if checkVersionPacket(packet):
                self.versionChecked = VERSION_CHECK_STATE.SUCCESS
            else:
                self.versionChecked = VERSION_CHECK_STATE.FAILURE
                print('Board reported an unsupported hardware or software revision.')
            return
        if not self.versionChecked == VERSION_CHECK_STATE.SUCCESS:
            # Don't process any packets until we are sure we know how to talk to this board
            return
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
        if not self.versionChecked:
            # This method should never be called if a version check hasn't passed, but just in case...
            print('Attempted to fire without version check!')
            return
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
