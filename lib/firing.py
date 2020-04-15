from enum import Enum
from math import ceil

from PyQt5.QtCore import QObject, pyqtSignal

from .converter import Converter
from .radio import RadioManager, SetupPacket, FirePacket, ResultPacket, ErrorPacket, StopPacket, VersionPacket
from .motor import processRawData
from .firmwareVersions import checkVersionPacket
from .logger import logger


PACKET_STRIDE = 10

class VERSION_CHECK_STATE(Enum):
    UNCHECKED = 1
    SUCCESS = 2
    FAILURE = 3


class Firing(QObject):
    newGraph = pyqtSignal(object)
    newSetupPacket = pyqtSignal(object)
    newErrorPacket = pyqtSignal(object)

    fullSizeKnown = pyqtSignal(int)
    newResultsPacket = pyqtSignal()

    fired = pyqtSignal()
    stopped = pyqtSignal()
    hasResults = pyqtSignal()

    def __init__(self, forceConverter, pressureConverter, motorInfo, port):
        super().__init__()
        self.versionChecked = VERSION_CHECK_STATE.UNCHECKED

        self.rawData = {}
        self.startIndex = None
        self.lastSend = 0
        self.lastSequenceMod = None
        self.fullSize = None

        self.forceConverter = forceConverter
        self.pressureConverter = pressureConverter
        self.motorInfo = motorInfo

        self.radioManager = RadioManager()
        self.radioManager.newPacket.connect(self.newPacket)
        self.radioManager.run(port)

    def processAndSend(self):
        logger.log('Processing more data ({}->{})'.format(self.lastSend, len(self.rawData)))
        raw = {'time': [], 'force': [], 'pressure': []}

        recv = list(self.rawData.keys())
        recv.sort()
        for i in recv:
            raw['time'].append(self.rawData[i].time)
            raw['force'].append(self.rawData[i].force)
            raw['pressure'].append(self.rawData[i].pressure)
        self.lastSend = len(self.rawData)

        self.newGraph.emit(processRawData(raw, self.forceConverter, self.pressureConverter, self.motorInfo))


    def newPacket(self, packet):
        if type(packet) is VersionPacket and self.versionChecked == VERSION_CHECK_STATE.UNCHECKED:
            if checkVersionPacket(packet):
                logger.log('Board version check passed ({})'.format(packet))
                self.versionChecked = VERSION_CHECK_STATE.SUCCESS
            else:
                logger.error('Board version check failed ({})'.format(packet))
                self.versionChecked = VERSION_CHECK_STATE.FAILURE
            return
        if not self.versionChecked == VERSION_CHECK_STATE.SUCCESS:
            # Don't process any packets until we are sure we know how to talk to this board
            return
        if type(packet) is SetupPacket:
            self.newSetupPacket.emit(packet)
        elif type(packet) is ErrorPacket:
            self.newErrorPacket.emit(packet)
        elif type(packet) is ResultPacket:
            self.newResultsPacket.emit()
            self.rawData[packet.seqNum] = packet
            if len(self.rawData) == 1:
                logger.log('Got first result packet, setting start index to {}'.format(packet.seqNum))
                self.startIndex = packet.seqNum
            else:
                if self.lastSend == 0 and abs(packet.seqNum - self.startIndex) < PACKET_STRIDE:
                    logger.log('Latest seq num ({}) close to start index ({})'.format(packet.seqNum, self.startIndex))
                    # The number of datapoints in a recording is always a multiple of 64 so we can figure out the
                    # size of the recording from the partial data assuming we got one of the last 64 datapoints.
                    # If not, it isn't a big deal because only the progress bar is impacted.
                    self.fullSize = ceil(max(self.rawData.keys()) / 64) * 64
                    self.fullSizeKnown.emit(self.fullSize)
                    self.lastSequenceMod = packet.seqNum % PACKET_STRIDE
                    self.processAndSend()

                diffSeqMod = self.lastSequenceMod is not None and packet.seqNum % PACKET_STRIDE != self.lastSequenceMod
                if diffSeqMod and len(self.rawData) > self.lastSend and self.motorInfo is not None:
                    self.lastSequenceMod = packet.seqNum % PACKET_STRIDE
                    self.processAndSend()
                    if self.lastSend == self.fullSize:
                        logger.log('Done receiving data')
                        self.radioManager.stop()

    def fire(self):
        if not self.versionChecked:
            # This method should never be called if a version check hasn't passed, but just in case...
            logger.error('Attempted to fire without version check!')
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
