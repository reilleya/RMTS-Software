from scipy import stats
from PyQt5.QtCore import QObject, pyqtSignal

from .radio import RadioManager, SetupPacket, ErrorPacket
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
    errorPacket = pyqtSignal(object)

    ready = pyqtSignal()
    done = pyqtSignal()

    resetDataAge = pyqtSignal()

    newInfo = pyqtSignal(object)
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

        self.tare = []

    def connect(self):
        self.radioManager.run(self.port)

    def updateInfo(self, properties):
        self.converter.setProperties(properties)
        self.newInfo.emit(properties)

    def newPacket(self, packet):
        self.resetDataAge.emit()
        if type(packet) is SetupPacket:
            if not self.gotSetupPacket:
                self.gotSetupPacket = True
                self.ready.emit()
            if self.converter.getProperty('type') == 'Load Cell':
                if len(self.tare) < 10:
                    self.tare.append(packet.pressure)
                else: 
                    logger.log((packet.pressure - (sum(self.tare) / len(self.tare))) * 1.58908799 * 0.000145038 * 2.2425)
                value = packet.force
            else:
                value = packet.pressure
            self.newReading.emit(int(self.filter.addData(value)))
        elif type(packet) is ErrorPacket:
            self.errorPacket.emit(packet)

    def capture(self):
        last = self.filter.getValue()
        if last is not None:
            point = CalibrationPoint(last, None)
            self.points.append(point)
            self.newPoints.emit(self.points)
            logger.log('Captured a point at {}'.format(last))

    def setReal(self, point, value):
        self.points[point].converted = value
        logger.log('Set the real value of {} to {}'.format(self.points[point].raw, value))
        self.updateRegression()

    def delete(self, point):
        del self.points[point]
        self.newPoints.emit(self.points)
        self.updateRegression()

    def updateRegression(self):
        graphPoints = [[], []]
        for point in self.points:
            if point.valid():
                graphPoints[0].append(point.raw)
                graphPoints[1].append(point.converted)

        if len(graphPoints[0]) > 0:
            self.newGraphPoints.emit(graphPoints)

        if len(graphPoints[0]) > 2:
            slope, intercept, rVal, p_value, std_err = stats.linregress(graphPoints[0], graphPoints[1])
            logger.log('Calculated slope {:.6f} and int. {:.6f}, r**2 = {:.6f}'.format(slope, intercept, rVal**2))
            self.newRegression.emit([graphPoints[0], [intercept + p * slope for p in graphPoints[0]], rVal])
            self.converter.setProperty('ratio', slope)
            self.converter.setProperty('offset', intercept)
            self.newConverter.emit(self.converter)
        else:
            self.newRegression.emit(None)
            self.newConverter.emit(None)

    def exit(self):
        self.radioManager.stop()
