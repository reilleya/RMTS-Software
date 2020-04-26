import sys

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal

from pyFormGen.units import convert
from pyFileIO import fileIO

from lib.sensorProfileManager import SensorProfileManager
from lib.preferencesManager import PreferencesManager
from lib.logger import logger
from lib.fileTypes import FILE_TYPES
from ui.mainWindow import MainWindow

class App(QApplication):

    NAME = 'RMTS'
    VERSION = (0, 1, 0)

    newConverter = pyqtSignal(object)
    newFiringConfig = pyqtSignal(object)

    def __init__(self, args):
        super().__init__(args)
        self.setupFileIO()
        self.sensorProfileManager = SensorProfileManager()
        self.sensorProfileManager.loadProfiles()
        self.preferencesManager = PreferencesManager()
        self.preferencesManager.loadPreferences()

        self.window = MainWindow(self)
        logger.log('Showing window')
        self.window.show()

    def outputMessage(self, content, title='RMTSI'):
        msg = QMessageBox()
        msg.setText(content)
        msg.setWindowTitle(title)
        msg.exec_()

    def outputException(self, exception, text, title='RMTSI - Error'):
        msg = QMessageBox()
        msg.setText(text)
        msg.setInformativeText(str(exception))
        msg.setWindowTitle(title)
        msg.exec_()

    def convertToUserUnits(self, value, units):
        return self.preferencesManager.preferences.convert(value, units)

    def convertFromUserUnits(self, value, baseUnit):
        inUnit = self.preferencesManager.preferences.getUnit(baseUnit)
        return convert(value, inUnit, baseUnit)

    def convertAllToUserUnits(self, values, units):
        return self.preferencesManager.preferences.convertAll(values, units)

    def convertToUserAndFormat(self, value, units, places):
        return self.preferencesManager.preferences.convFormat(value, units, places)

    def getUserUnit(self, unit):
        return self.preferencesManager.preferences.getUnit(unit)

    def getPreferences(self):
        return self.preferencesManager.preferences

    def newResult(self, motorInfo):
        self.window.ui.pageResults.showResults(motorInfo)

    def configureLiveResults(self, size):
        self.window.ui.pageResults.setupLive(size)

    # No packet argument because this is just for resetting data age
    def newResultsPacket(self):
        self.window.ui.pageResults.newResultsPacket()

    def newCalibration(self, calibration):
        self.window.ui.pageCalibration.newCalibration(calibration)

    def setupFileIO(self):
        fileIO.setAppInfo(self.NAME, self.VERSION)
        fileIO.registerFileType(FILE_TYPES.PREFERENCES)
        fileIO.registerFileType(FILE_TYPES.TRANSDUCERS)
        fileIO.registerFileType(FILE_TYPES.FIRING)
