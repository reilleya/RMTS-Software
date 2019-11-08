import math

from PyQt5.QtCore import QObject, pyqtSignal

PACKET_STRIDE = 10

class MotorResults():
    def __init__(self, time, force, pressure, startupTime, propMass, nozzleThroat):
        self.time = time
        self.force = force
        self.pressure = pressure
        self.numDataPoints = len(time)

        self.startupTime = startupTime
        self.propMass = propMass
        self.nozzleThroat = nozzleThroat

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

class Firing(QObject):
    """Contains the results of a single firing """

    newGraph = pyqtSignal(object)

    def __init__(self, converter):
        super().__init__()
        self.origin = 'radio'
        self.rawData = {}
        self.startIndex = None
        self.lastSend = 0

        self.converter = converter

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
        while f[endCutoff] > 0.05 * maxForce:
            endCutoff += 1
        endCutoff = min(endCutoff + 10, len(f))

        t, f, p = t[:endCutoff], f[:endCutoff], p[:endCutoff]

        startCutoff = f.index(maxForce)
        while f[startCutoff] > 0.05 * maxForce:
            startCutoff -= 1
        endCutoff = max(startCutoff - 15, 0)

        t, f, p = t[startCutoff:], f[startCutoff:], p[startCutoff:]

        burnTime = t[-1] - t[0]
        startupTransient = t[0]
        t = [d - t[0] for d in t]

        return MotorResults(t, f, p, startupTransient, 0.6, 0)

    def addDatapoint(self, packet):
        self.rawData[packet.seqNum] = packet
        if len(self.rawData) == 1:
            self.startIndex = packet.seqNum
        elif abs(packet.seqNum - self.startIndex) < PACKET_STRIDE:
            if len(self.rawData) > self.lastSend:
                res = self.processRawData()
                self.lastSend = len(self.rawData)
                self.newGraph.emit(res)

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

