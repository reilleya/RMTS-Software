from scipy import stats
from PyQt5.QtCore import QObject, pyqtSignal

from .radio import RadioManager, SetupPacket
from .filter import LowPass
from .converter import Converter
from .logger import logger

class CalibrationPoint():
    def __init__(self, raw, converted):
        self.raw = raw
        self.converted = converted

    def valid(self):
        return self.raw is not None and self.converted is not None

class Calibration(QObject):
    ready = pyqtSignal()
    done = pyqtSignal()

    resetDataAge = pyqtSignal()

    newReading = pyqtSignal(int)
    newPoints = pyqtSignal(list)
    newGraphPoints = pyqtSignal(object)
    newRegression = pyqtSignal(object)
    newConverter = pyqtSignal(object)

    def __init__(self, port, baseConfig):
        super().__init__()
        self.port = port
        self.filter = LowPass(5)

        self.radioManager = RadioManager()
        self.radioManager.newPacket.connect(self.newPacket)

        self.points = []
        self.converter = Converter(baseConfig)
        self.gotSetupPacket = False

    def connect(self):
        self.radioManager.run(self.port)

    def updateInfo(self, properties):
        self.converter.setProperties(properties)

    def newPacket(self, packet):
        self.resetDataAge.emit()
        if type(packet) is SetupPacket:
            if not self.gotSetupPacket:
                self.gotSetupPacket = True
                self.ready.emit()
            if self.converter.getProperty('type') == 'Load Cell':
                value = packet.force
            else:
                value = packet.pressure
            self.newReading.emit(int(self.filter.addData(value)))

    def capture(self):
        last = self.filter.getValue()
        if last is not None:
            point = CalibrationPoint(last, None)
            self.points.append(point)
            self.newPoints.emit(self.points)

    def setReal(self, point, value):
        self.points[point].converted = value
        self.emitGraphPoints()

    def delete(self, point):
        del self.points[point]
        self.newPoints.emit(self.points)
        self.emitGraphPoints()

    def emitGraphPoints(self):
        graphPoints = [[], []]
        for point in self.points:
            if point.valid():
                graphPoints[0].append(point.raw)
                graphPoints[1].append(point.converted)
        if len(graphPoints[0]) > 0:
            self.newGraphPoints.emit(graphPoints)

        if len(graphPoints[0]) > 2:
            slope, intercept, rVal, p_value, std_err = stats.linregress(graphPoints[0], graphPoints[1])
            logger.log(slope)
            logger.log(intercept)
            self.newRegression.emit([graphPoints[0], [intercept + p * slope for p in graphPoints[0]], rVal])
            self.converter.setProperty('ratio', slope)
            self.converter.setProperty('offset', intercept)
            self.newConverter.emit(self.converter)
        else:
            self.newRegression.emit(None)
            self.newConverter.emit(None)

    def exit(self):
        self.radioManager.stop()
