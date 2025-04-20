import sys
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from pyFormGen.units import convert, getConversion
from pyFileIO import fileIO

from lib.sensorProfileManager import SensorProfileManager
from lib.preferencesManager import PreferencesManager
from lib.logger import logger
from lib.fileTypes import FILE_TYPES
from lib.migrations import *

from ui.mainWindow import MainWindow

class App(QApplication):

    NAME = 'RMTS'
    VERSION = (0, 4, 0)

    newConverter = pyqtSignal(object)
    newFiringConfig = pyqtSignal(object)

    def __init__(self, args):
        super().__init__(args)

        self.icon = QIcon('resources/icon.png')

        if self.isDarkMode():
            # Change these settings before any graph widgets are built, so they apply everywhere
            plt.style.use('dark_background')
            mpl.rcParams['axes.facecolor'] = '1e1e1e'
            mpl.rcParams['figure.facecolor'] = '1e1e1e'

        self.setupFileIO()
        self.sensorProfileManager = SensorProfileManager()
        self.sensorProfileManager.loadProfiles()
        self.preferencesManager = PreferencesManager()
        self.preferencesManager.loadPreferences()

        logger.log('Application version: {}.{}.{}'.format(*self.VERSION))

        usingDarkMode = self.isDarkMode()
        currentTheme = self.style().objectName()
        logger.log('Opening window (dark mode: {}, default theme: "{}")'.format(usingDarkMode, currentTheme))
        # Windows 10 and before don't have dark mode versions of their themes, so if the user wants dark mode, we have to switch to fusion
        if usingDarkMode and currentTheme in ['windows', 'windowsvista']:
            logger.log('Overriding theme to fusion to get dark mode')
            self.setStyle('fusion')

        self.window = MainWindow(self)
        self.window.show()

    def isDarkMode(self):
        return self.styleHints().colorScheme() == Qt.ColorScheme.Dark

    def getLogoPath(self):
        return os.path.join(os.path.dirname(sys.argv[0]), 'resources/logo_large_light.svg' if self.isDarkMode() else 'resources/logo_large.svg')

    def outputMessage(self, content, title='RMTS'):
        msg = QMessageBox()
        msg.setText(content)
        msg.setWindowTitle(title)
        msg.setWindowIcon(self.icon)
        msg.exec()

    def outputException(self, exception, text, title='RMTS - Error'):
        msg = QMessageBox()
        msg.setText(text)
        msg.setInformativeText(str(exception))
        msg.setWindowTitle(title)
        msg.setWindowIcon(self.icon)
        msg.exec()

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

    # This is really gross, but because ft/s is an impractical unit for burn rate,
    # we override the user's preference to in/s if they have ft/s set
    def getBurnRateUnit(self):
        configuredUnit = self.getUserUnit('m/s')
        if configuredUnit in ('ft/s', 'in/s'):
            return 'in/s'
        if configuredUnit in ('m/s', 'cm/s', 'mm/s'):
            return 'mm/s'
        return configuredUnit

    def getBurnRateCoefficientUnit(self):
        lengthUnit = 'mm' if self.getBurnRateUnit() == 'mm/s' else 'in'

        return lengthUnit, self.getUserUnit('Pa')

    def getBurnRateCoefficientUnitString(self):
        return '{}/(s*{}^n)'.format(*self.getBurnRateCoefficientUnit())

    # Another gross one! Burn rate coefficient can't be converted like other units because of the exponent, so we do it here
    def convertBurnRateCoefficientToUserUnits(self, a, n):
        lengthUnit, pressureUnit = self.getBurnRateCoefficientUnit()
        return getConversion('m', lengthUnit) * a * (getConversion(pressureUnit, 'Pa') ** n)

    def getPreferences(self):
        return self.preferencesManager.preferences

    def newResult(self, motorInfo, fileName = None):
        self.window.ui.pageResults.showResults(motorInfo, fileName)

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

        fileIO.registerMigration(FILE_TYPES.PREFERENCES, (0, 1, 0), (0, 2, 0), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.TRANSDUCERS, (0, 1, 0), (0, 2, 0), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.FIRING, (0, 1, 0), (0, 2, 0), migrateFiring_0_1_0_to_0_2_0)

        fileIO.registerMigration(FILE_TYPES.PREFERENCES, (0, 2, 0), (0, 3, 0), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.TRANSDUCERS, (0, 2, 0), (0, 3, 0), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.FIRING, (0, 2, 0), (0, 3, 0), lambda data: data)

        fileIO.registerMigration(FILE_TYPES.PREFERENCES, (0, 3, 0), (0, 3, 1), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.TRANSDUCERS, (0, 3, 0), (0, 3, 1), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.FIRING, (0, 3, 0), (0, 3, 1), lambda data: data)

        fileIO.registerMigration(FILE_TYPES.PREFERENCES, (0, 3, 1), (0, 3, 2), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.TRANSDUCERS, (0, 3, 1), (0, 3, 2), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.FIRING, (0, 3, 1), (0, 3, 2), lambda data: data)

        fileIO.registerMigration(FILE_TYPES.PREFERENCES, (0, 3, 2), (0, 4, 0), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.TRANSDUCERS, (0, 3, 2), (0, 4, 0), lambda data: data)
        fileIO.registerMigration(FILE_TYPES.FIRING, (0, 3, 2), (0, 4, 0), lambda data: data)
