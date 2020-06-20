import serial
import time
from threading import Thread

from PyQt5.QtCore import QObject, pyqtSignal

from .errors import formatErrorMessage
from .logger import logger

class RadioRecvPacket():
    def __init__(self, data):
        if data is None:
            return
        self.type = data[0]
        self.checksum = data[1]
        self.seqNum = self.interpret16Bit(data[2:4])
        self.payload = data[4:12]

    def interpret24Bit(self, data):
        low = data[0]
        mid = data[1]
        high = data[2]
        return (low) + (mid * (2**8)) + (high * (2**16))

    def interpret16Bit(self, data):
        low = data[0]
        high = data[1]
        return (low) + (high * (2**8))

class RadioSendPacket():
    def __init__(self, packetType, seqNum):
        self.type = packetType
        self.seqNum = seqNum

    def pack16Bit(self, value):
        return [value & 0xFF, (value >> 8 & 0xFF)]

    def padPayload(self, payload):
        return payload + [0 for i in range(0, 8 - len(payload))]

    def getPayload(self):
        raise Exception("Not implemented")

    def __str__(self):
        return "Unlabeled packet with type {}".format(self.type)

class SetupPacket(RadioRecvPacket):
    def __init__(self, data):
        super().__init__(data)
        self.force = self.interpret24Bit(self.payload[0:])
        self.pressure = self.interpret24Bit(self.payload[3:])
        self.continuity = bool(self.payload[6])

    def __str__(self):
        return "Force: {}, Pressure: {}, Continuity: {}".format(self.force, self.pressure, self.continuity)

class VersionPacket(RadioRecvPacket):
    def __init__(self, data):
        super().__init__(data)
        self.firmwareVersion = self.interpret16Bit(self.payload[0:2])
        self.hardwareVersion = self.payload[2]

    def __str__(self):
        return "Hardware Version: {}, Firmware Version: {}".format(self.hardwareVersion, self.firmwareVersion)

class FiringPacket(RadioRecvPacket):
    def __init__(self, data):
        super().__init__(data)
        self.force = self.interpret24Bit(self.payload[0:])
        self.pressure = self.interpret24Bit(self.payload[3:])
        self.time = self.payload[6] + ((self.payload[7] & 0xFE) * (2 ** 7))
        self.continuity = bool(self.payload[7] & 0b1)

    def __str__(self):
        return "Force: {}, Pressure: {}, Time: {}, Continuity: {}".format(self.force, self.pressure, self.time, self.continuity)


class ErrorPacket(RadioRecvPacket):
    def __init__(self, data):
        super().__init__(data)
        self.storageError = self.payload[0]
        self.adcError = self.payload[1]

    def __str__(self):
        out = "Storage: {}, ADC: {}".format(self.storageError, self.adcError)
        return out

    # Returns a list of error strings for all devices that are not nominal (err = 0)
    def getErrors(self):
        errors = [self.storageError, self.adcError]
        strErrors = [formatErrorMessage(device, code) for device, code in enumerate(errors)]
        return [error for index, error in enumerate(strErrors) if errors[index] != 0]

    # Returns an ordered list of device error codes
    def getErrorList(self):
        return [self.storageError, self.adcError, 0] # Radio errors are currently not sent

class ResultPacket(RadioRecvPacket):
    def __init__(self, data):
        super().__init__(data)
        if data is None:
            return
        self.time = self.interpret16Bit(self.payload)
        self.force = self.interpret24Bit(self.payload[2:])
        self.pressure = self.interpret24Bit(self.payload[5:])

    def __str__(self):
        out = "#: {}, Time: {}, Force: {}, Pressure: {}".format(self.seqNum, self.time, self.force, self.pressure)
        return out

    def validate(self):
        timeValid = 5 + (6 * self.seqNum) < self.time < 15 + (7 * self.seqNum)
        forceValid = 0 <= self.force <= 0x7FFFFF
        pressureValid = 0 <= self.pressure <= 0x7FFFFF
        return timeValid and forceValid and pressureValid


class FirePacket(RadioSendPacket):
    def __init__(self, fireDuration):
        super().__init__(128, 0)
        self.fireDuration = fireDuration

    def getPayload(self):
        # First 16 bits is the deprecated recording time
        payload = self.pack16Bit(0) + self.pack16Bit(self.fireDuration)
        return self.padPayload(payload)

    def __str__(self):
        return 'Fire packet, duration = {} ms'.format(self.fireDuration)

class StopPacket(RadioSendPacket):
    def __init__(self):
        super().__init__(129, 0)

    def getPayload(self):
        return self.padPayload([])

    def __str__(self):
        return "Stop packet"

class CalStartPacket(RadioSendPacket):
    def __init__(self):
        super().__init__(130, 0)

    def getPayload(self):
        return self.padPayload([])

class CalStopPacket(RadioSendPacket):
    def __init__(self):
        super().__init__(131, 0)

    def getPayload(self):
        return self.padPayload([])


class RadioManager(QObject):
    PACKET_SIZE = 12
    PREAMBLE = [0xAA, 0xBB]
    ESCAPE = 0x11

    PACKET_TYPE_MAP = {
        0: SetupPacket,
        1: ErrorPacket,
        2: ResultPacket,
        3: VersionPacket,
        4: FiringPacket
    }

    newPacket = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.toSend = []
        self.clearOutputBuffer = False
        self.port = None
        self._lastPacketRecv = 0
        self.setupSerialThread()

    @staticmethod
    def checkPacket(packet):
        checksum = (sum(packet) % 256) == 0
        rightLength = len(packet) == RadioManager.PACKET_SIZE
        return checksum and rightLength

    def sendPacket(self, packet, resendCount=5):
        logger.log('Sending packet with details ({}) {} times'.format(packet, resendCount))
        seqNumLow = packet.seqNum & 0xFF
        seqNumHigh = (packet.seqNum >> 8) & 0xFF
        pack = [packet.type, 0, seqNumLow, seqNumHigh] + packet.getPayload()
        pack[1] = (256 - sum(pack)) % 256
        for i in range(0, resendCount):
            self.toSend.append(bytearray(RadioManager.PREAMBLE + pack))

    def clearSendBuffer(self):
        self.clearOutputBuffer = True

    def buildPacket(self, packetData):
        if packetData[0] not in RadioManager.PACKET_TYPE_MAP.keys():
            logger.error('Invalid packet with type {} received'.format(packetData[0]))
            return
        packetCons = RadioManager.PACKET_TYPE_MAP[packetData[0]]
        pack = packetCons(packetData)
        self.newPacket.emit(pack)

    def setupSerialThread(self):
        self.serialThread = Thread(target=self._serialThread)
        self.running = False
        self.closed = False

    def _serialThread(self):
        with serial.Serial(self.port, 9600) as serport:
            logger.log('Connected to radio on port ({})'.format(self.port))
            self.closed = False
            escape = False
            packetBuff = []
            inPreamble = False
            inPacket = False
            while self.running:
                while serport.in_waiting > 0 and len(self.toSend) == 0:
                    b = int.from_bytes(serport.read(), 'big')
                    if b == RadioManager.PREAMBLE[0] and not escape:
                        inPreamble = True
                        inPacket = False
                    elif b == RadioManager.PREAMBLE[1] and not escape and inPreamble:
                        packetBuff = []
                        inPacket = True
                    elif inPacket and (b != RadioManager.ESCAPE or escape):
                        packetBuff.append(b)
                        if self.checkPacket(packetBuff):
                            self.buildPacket(packetBuff)
                            inPacket = False
                    escape = b == RadioManager.ESCAPE and not escape

                if len(self.toSend) > 0:
                    packet = self.toSend.pop(0)
                    serport.write(packet)

                if self.clearOutputBuffer:
                    self.toSend = []
                    self.clearOutputBuffer = False

        self.closed = True
        logger.log('Serial thread exited')

    def run(self, port):
        if self.running:
            self.stop()
            self.setupSerialThread()
            while not self.closed and port == self.port:
                logger.warn("Waiting for port to close before reopening.")
                pass
        self.port = port
        self.running = True
        self.serialThread.start()

    def stop(self):
        self.running = False

    def runCalibration(self):
        calThread = Thread(target=self._calibrationThread)
        calThread.start()

    def _calibrationThread(self):
        self.sendPacket(CalStartPacket())
        time.sleep(1)
        self.sendPacket(CalStopPacket())
