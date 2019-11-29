import math

from pyFormGen.properties import PropertyCollection, FloatProperty, EnumProperty
from PyQt5.QtCore import QObject, pyqtSignal

PACKET_STRIDE = 10

class MotorConfig(PropertyCollection):
    def __init__(self):
        super().__init__()
        self.props['motorOrientation'] = EnumProperty('Motor Orientation', ['Vertical', 'Horizontal'])
        self.props['propellantMass'] = FloatProperty('Propellant Mass', 'kg', 0.01, 100)
        self.props['throatDiameter'] = FloatProperty('Throat Diameter', 'm', 0.0001, 1)

class FiringConfig(MotorConfig):
    def __init__(self):
        super().__init__()
        self.props['recordingDuration'] = FloatProperty('Recording Duration', 's', 5, 20)
        self.props['firingDuration'] = FloatProperty('Fire Duration', 's', 0.25, 3)

    def getMotorInfo(self):
        motorConfig = MotorConfig()
        motorConfig.setProperties(self.getProperties())
        return motorConfig

class MotorResults():
    def __init__(self, time, force, pressure, startupTime, motorInfo, rawData):
        self.time = time
        self.force = force
        self.pressure = pressure
        self.numDataPoints = len(time)

        self.startupTime = startupTime
        self.motorInfo = motorInfo
        self.propMass = self.motorInfo.getProperty('propellantMass')
        self.nozzleThroat = self.motorInfo.getProperty('throatDiameter')

    def getTime(self):
        return self.time

    def getPressure(self):
        return self.pressure

    def getForce(self):
        return self.force

    def getImpulse(self):
        totalImpulse = 0
        for i in range(1, self.numDataPoints):
            totalImpulse += (self.time[i] - self.time[i - 1]) * (self.force[i] + self.force[i - 1]) / 2
        return totalImpulse

    def getBurnTime(self):
        return self.time[-1]

    def getStartupTime(self):
        return self.startupTime

    def getPropMass(self):
        return self.propMass

    def getPeakThrust(self):
        return max(self.force)

    def getAverageThrust(self):
        return self.getImpulse() / self.getBurnTime()

    def getMotorDesignation(self):
        imp = self.getImpulse()
        if imp < 1.25: # This is to avoid a domain error finding log(0)
            return 'N/A'
        return chr(int(math.log(imp/1.25, 2)) + 65) + str(int(self.getAverageThrust()))

    def getISP(self):
        return self.getImpulse() / (self.getPropMass() * 9.81)

    def getCSV(self):
        forceUnit = 'N'
        pressureUnit = 'Pa'
        out = 'time(s),force({}),pressure({})'.format(forceUnit, pressureUnit)
        for i in range(0, self.numDataPoints):
            convTime = round(self.time[i], 4)
            convForce = round(self.force[i], 4)
            convPressure = round(self.pressure[i], 4)
            out+= "\n{},{},{}".format(convTime, convForce, convPressure)
        return out

class Firing(QObject):
    """Contains the results of a single firing """

    newGraph = pyqtSignal(object)

    def __init__(self, converter=None, motorInfo=None):
        super().__init__()
        self.origin = 'radio'
        self.rawData = {}
        self.startIndex = None
        self.lastSend = 0

        self.converter = converter
        self.motorInfo = motorInfo

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

        t = [d / 1000 for d in t]
        f = self.converter.convertForces(f)
        p = self.converter.convertPressures(p)

        maxForce = max(f)
        endCutoff = f.index(maxForce)
        while f[endCutoff] > 0.05 * maxForce and endCutoff < len(f) - 1:
            endCutoff += 1
        endCutoff = min(endCutoff + 10, len(f))

        t, f, p = t[:endCutoff], f[:endCutoff], p[:endCutoff]

        startCutoff = f.index(maxForce)
        while f[startCutoff] > 0.05 * maxForce and startCutoff > 0:
            startCutoff -= 1
        endCutoff = max(startCutoff - 15, 0)

        t, f, p = t[startCutoff:], f[startCutoff:], p[startCutoff:]

        burnTime = t[-1] - t[0]
        startupTransient = t[0]
        t = [d - t[0] for d in t]

        return MotorResults(t, f, p, startupTransient, self.motorInfo, self.rawData)

    def addDatapoint(self, packet):
        self.rawData[packet.seqNum] = packet
        if len(self.rawData) == 1:
            self.startIndex = packet.seqNum
        elif abs(packet.seqNum - self.startIndex) < PACKET_STRIDE:
            if len(self.rawData) > self.lastSend and self.motorInfo is not None:
                res = self.processRawData()
                self.lastSend = len(self.rawData)
                self.newGraph.emit(res)

    def setMotorInfo(self, info):
        self.motorInfo = info
        if len(self.rawData) > 0:
            self.newGraph.emit(self.processRawData())

    # TODO: Precalculate these when data comes in
    def getRawTime(self):
        recv = list(self.rawData.keys())
        recv.sort()
        t = []
        for i in recv:
            t.append(self.rawData[i].time)
        return t

    def getRawForce(self):
        recv = list(self.rawData.keys())
        recv.sort()
        f = []
        for i in recv:
            f.append(self.rawData[i].force)
        return f

    def getRawPressure(self):
        recv = list(self.rawData.keys())
        recv.sort()
        p = []
        for i in recv:
            p.append(self.rawData[i].pressure)
        return p
