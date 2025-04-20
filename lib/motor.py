import math

from pyFormGen.properties import PropertyCollection, FloatProperty, EnumProperty
from .logger import logger

class MotorConfig(PropertyCollection):
    def __init__(self, propDict=None):
        super().__init__()
        self.props['motorOrientation'] = EnumProperty('Motor Orientation', ['Vertical', 'Horizontal'])
        self.props['propellantMass'] = FloatProperty('Propellant Mass', 'kg', 0.01, 100)
        self.props['throatDiameter'] = FloatProperty('Throat Diameter', 'm', 0.0001, 1)
        self.props['cutoffThreshold'] = FloatProperty('Cutoff', '%', 0.1, 99.9)

        if propDict is not None:
            self.setProperties(propDict)

class FiringConfig(MotorConfig):
    def __init__(self, propDict=None):
        super().__init__()
        self.props['firingDuration'] = FloatProperty('Fire Duration', 's', 0.25, 3)

        if propDict is not None:
            self.setProperties(propDict)

    def getMotorInfo(self):
        motorConfig = MotorConfig()
        motorConfig.setProperties(self.getProperties())
        return motorConfig

class MotorResults():
    def __init__(self, time, force, pressure, startupTime, motorInfo, rawData, forceConv, presConv):
        self.time = time
        self.force = force
        self.pressure = pressure
        self.numDataPoints = len(time)

        self.startupTime = startupTime
        self.motorInfo = motorInfo
        self.forceConv = forceConv
        self.presConv = presConv
        self.propMass = self.motorInfo.getProperty('propellantMass')
        self.nozzleThroat = self.motorInfo.getProperty('throatDiameter')
        self.raw = rawData

    def hasForceConverter(self):
        return self.forceConv is not None

    def hasPressureConverter(self):
        return self.presConv is not None

    def getNumDataPoints(self):
        return self.numDataPoints

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
        if self.getBurnTime() == 0:
            return 0
        return self.getImpulse() / self.getBurnTime()

    def getPeakPressure(self):
        return max(self.pressure)

    def getIntegratedPressure(self):
        totalPressure = 0
        for i in range(1, self.numDataPoints):
            totalPressure += (self.time[i] - self.time[i - 1]) * (self.pressure[i] + self.pressure[i - 1]) / 2
        return totalPressure

    def getAveragePressure(self):
        if self.getBurnTime() == 0:
            return 0
        return self.getIntegratedPressure() / self.getBurnTime()

    def getThroatArea(self):
        return 3.14159 * (self.nozzleThroat / 2)**2

    def getCStar(self):
        return self.getThroatArea() * self.getIntegratedPressure() / self.propMass

    def getThrustCoefficient(self):
        throatArea = self.getThroatArea()
        modPressure = [pressure if abs(pressure) != 0 else 1E-6 for pressure in self.getPressure()]
        cf = [thrust / (throatArea * pressure) for thrust, pressure in zip(self.getForce(), modPressure)]
        cf.sort()
        return cf[int(len(cf) / 2)]

    def getMotorDesignation(self):
        imp = self.getImpulse()
        if imp < 1.25: # This is to avoid a domain error finding log(0)
            return 'N/A'
        return chr(int(math.log(imp/1.25, 2)) + 65) + str(int(self.getAverageThrust()))

    def getISP(self):
        return self.getImpulse() / (self.getPropMass() * 9.81)

    def getRawTime(self):
        return self.raw['time']

    def getRawForce(self):
        return self.raw['force']

    def getRawPressure(self):
        return self.raw['pressure']

    def getCSV(self):
        out = 'time(s)'
        if self.hasForceConverter():
            out += ',force({})'.format('N')
        if self.hasPressureConverter():
            out += ',pressure({})'.format('Pa')
        for i in range(0, self.numDataPoints):
            out += '\n{:.4f}'.format(self.time[i])
            if self.hasForceConverter():
                out += ',{:.4f}'.format(self.force[i])
            if self.hasPressureConverter():
                out += ',{:.4f}'.format(self.pressure[i])
        return out

    def getRawCSV(self):
        out = 'time(ms),force(counts),pressure(counts)'
        for i in range(0, len(self.raw['time'])):
            out += "\n{},{},{}".format(self.raw['time'][i], self.raw['force'][i], self.raw['pressure'][i])
        return out

    def toDictionary(self):
        out = {
            'rawData': self.raw,
            'motorInfo': self.motorInfo.getProperties(),
            'forceConv': None if self.forceConv is None else self.forceConv.getProperties(),
            'pressureConv': None if self.presConv is None else self.presConv.getProperties()
        }
        return out

def rejectOutliers(d):
    # If a point is more than 2 times either of its neighbors, something is wrong and it should be smoothed out
    if len(d) > 3:
        for i in range(1, len(d) - 1):
            if (d[i] > 2 * d[i - 1] and d[i] > 2 * d[i + 1]):
                d[i] = (d[i - 1] + d[i + 1]) / 2
    return d

def getTrimPoints(channel, threshold):
    # Trim data from the end
    maxValue = max(channel)
    endCutoff = channel.index(maxValue)
    while channel[endCutoff] > threshold * maxValue and endCutoff < len(channel) - 1:
        endCutoff += 1
    endCutoff = min(endCutoff, len(channel))

    # Trim data from the start
    startCutoff = channel.index(maxValue)
    while channel[startCutoff] > threshold * maxValue and startCutoff > 0:
        startCutoff -= 1
    return startCutoff, endCutoff

NUM_CAL_FRAMES = 10

def processRawData(rawData, forceConv, presConv, motorInfo):
    t = rawData['time'][:]
    f = rawData['force'][:]
    p = rawData['pressure'][:]

    f = rejectOutliers(f)
    p = rejectOutliers(p)

    cutoff = motorInfo.getProperty('cutoffThreshold') / 100

    if len(t) == 0:
        raise ValueError('No datapoints')

    # Remove amplifier offset
    # Assumes that there are 10+ points before thrust begins. The firmware waits 10 before firing to make sure.
    if forceConv is not None:
        startupForces = f[:NUM_CAL_FRAMES]
        startupForces.sort()
        startupForcesAverage = startupForces[5]
        baseForce = forceConv.toRaw(0)
        logger.log('Startup force median: {}, conv: {}'.format(startupForcesAverage, forceConv.convert(startupForcesAverage)))
        f = [d - startupForcesAverage + baseForce for d in f]

    if presConv is not None:
        startupPressures = p[:NUM_CAL_FRAMES]
        startupPressures.sort()
        startupPressuresAverage = startupPressures[5]
        basePressure = presConv.toRaw(0)
        logger.log('Startup pressure median: {}, conv: {}'.format(startupPressuresAverage, presConv.convert(startupPressuresAverage)))
        p = [d - startupPressuresAverage + basePressure for d in p]

    t = t[NUM_CAL_FRAMES:]
    f = f[NUM_CAL_FRAMES:]
    p = p[NUM_CAL_FRAMES:]

    timesteps = [t[i] - t[i-1] for i in range(1, len(t))]
    logger.log('Timesteps: min={}, max={}, mean={:.4f}'.format(
        min(timesteps),
        max(timesteps),
        sum(timesteps) / len(timesteps))
    )

    # Convert to proper units
    t = [d / 1000 for d in t]
    if forceConv is not None:
        f = forceConv.convertMultiple(f)
    if presConv is not None:
        p = presConv.convertMultiple(p)

    if forceConv is not None:
        start, end = getTrimPoints(f, cutoff)
    else:
        start, end = getTrimPoints(p, cutoff)
    t, f, p = t[start:end], f[start:end], p[start:end]

    # Final adjustments and calculations
    burnTime = t[-1] - t[0]
    startupTransient = t[0] - (rawData['time'][NUM_CAL_FRAMES - 1] / 1000)
    t = [d - t[0] for d in t]
    if motorInfo.getProperty('motorOrientation') == 'Vertical':
        if burnTime == 0:
            burnTime = 0.01
        for i, time in enumerate(t):
            f[i] += (time / burnTime) * motorInfo.getProperty('propellantMass') * 9.81

    return MotorResults(t, f, p, startupTransient, motorInfo, rawData, forceConv, presConv)
