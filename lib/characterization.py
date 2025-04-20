import math
from scipy import stats
from PyQt6.QtCore import QObject, pyqtSignal

from pyFileIO import fileIO

from .logger import logger
from .converter import Converter
from .motor import processRawData, FiringConfig
from .fileTypes import FILE_TYPES

class CharacterizationMotor():
    def __init__(self, path, averagePressure, burnTime, cstar, web = None):
        self.path = path
        self.averagePressure = averagePressure
        self.web = web
        self.burnTime = burnTime
        self.cstar = cstar

    def getBurnRate(self):
        return self.web / self.burnTime

class CharacterizationResult():
    def __init__(self, a, n, r, cstar, cstarStdDev, minPressure, maxPressure):
        self.a = a
        self.n = n
        self.r = r
        self.cstar = cstar
        self.cstarStdDev = cstarStdDev
        self.minPressure = minPressure
        self.maxPressure = maxPressure

class Characterization(QObject):
    ready = pyqtSignal()
    done = pyqtSignal()

    firingListUpdated = pyqtSignal(list)
    characterizationPointsUpdated = pyqtSignal(list)
    characterizationResultCalculated = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.firings = []

    # Is this a fresh characterization run, or has the user done work?
    def inProgress(self):
        return len(self.firings) != 0

    def updateFiringWeb(self, firingIndex, web):
        logger.log('Setting firing "{}" web to "{}"'.format(firingIndex, web))
        self.firings[firingIndex].web = web
        self.runCharacterization()

    def loadFireFile(self, path):
        logger.log('Characterization loading motor from "{}"'.format(path))

        if path in [firing.path for firing in self.firings]:
            raise ValueError('Already loaded file')

        data = fileIO.load(FILE_TYPES.FIRING, path)
        if data['pressureConv'] is None:
            raise ValueError('File has no pressure data')

        motor = processRawData(data['rawData'],
                None if data['forceConv'] is None else Converter(data['forceConv']),
                None if data['pressureConv'] is None else Converter(data['pressureConv']),
                FiringConfig(data['motorInfo'])
            )

        motorStats = CharacterizationMotor(path, motor.getAveragePressure(), motor.getBurnTime(), motor.getCStar())
        self.firings.append(motorStats)
        logger.log('Loaded motor with stats C*="{}", burn time="{}"'.format(motorStats.cstar, motorStats.burnTime))
        self.firingListUpdated.emit(self.firings)
        self.runCharacterization()

    def runCharacterization(self):
        try:
            cstar, stdDev = self.calculateCStar()
            a, n, r = self.calculateRegression()
            minPressure, maxPressure = self.findPressureRange()
            self.characterizationResultCalculated.emit(CharacterizationResult(a, n, r, cstar, stdDev, minPressure, maxPressure))
        except Exception as e:
            logger.log('Unable to run characterization: {}'.format(e))

    def calculateRegression(self):
        firingsWithWebs = filter(lambda point: point.web is not None, self.firings)
        points = [(firing.averagePressure, firing.getBurnRate()) for firing in firingsWithWebs]
        self.characterizationPointsUpdated.emit(points) # TODO: refactor so this isn't buried in here

        if len(points) < 3:
            raise ValueError('Not enough points to run regression')

        xLogPoints = [math.log(point[0]) for point in points]
        yLogPoints = [math.log(point[1]) for point in points]

        slope, intercept, rVal, p_value, std_err = stats.linregress(xLogPoints, yLogPoints)
        a = math.e ** intercept
        n = slope

        return a, n, rVal

    def calculateCStar(self):
        cstars = [firing.cstar for firing in self.firings]
        average = sum(cstars) / len(cstars)
        stdDev = (sum([(sample - average) ** 2 for sample in cstars]) / len(cstars)) ** 0.5
        return average, stdDev

    def findPressureRange(self):
        pressures = [firing.averagePressure for firing in self.firings]
        return min(pressures), max(pressures)

    def removeFiring(self, firingIndex):
        del self.firings[firingIndex]
        self.firingListUpdated.emit(self.firings)
        self.runCharacterization()

    def setAllWebs(self, web):
        for firing in self.firings:
            firing.web = web
        self.firingListUpdated.emit(self.firings)
        self.runCharacterization()
