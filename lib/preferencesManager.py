from PyQt5.QtCore import QObject, pyqtSignal

from pyFileIO import fileIO
from pyFormGen.unitPreferences import UnitPreferences
from pyFormGen.collectionEditor import CollectionEditor
from .fileTypes import FILE_TYPES
from .logger import logger

class PreferencesManager(QObject):

    preferencesChanged = pyqtSignal()
    PREFERENCES_PATH = 'preferences.yaml'

    def __init__(self):
        super().__init__()
        self.preferences = UnitPreferences()

    def loadPreferences(self):
        try:
            self.preferences.setProperties(fileIO.loadFromDataDirectory(FILE_TYPES.PREFERENCES, self.PREFERENCES_PATH))
            self.preferencesChanged.emit()
        except Exception as err:
            logger.error('Could not read preferences, using default. Error: {}'.format(repr(err)))
            self.loadDefault()
            self.savePreferences()

    def savePreferences(self):
        logger.log('Saving preferences...')
        try:
            fileIO.saveToDataDirectory(FILE_TYPES.PREFERENCES, self.preferences.getProperties(), self.PREFERENCES_PATH)
        except Exception as err:
            logger.error('Could not save preferences. Error: {}'.format(repr(err)))

    def setPreferences(self, pref):
        self.preferences = pref
        self.preferencesChanged.emit()
        self.savePreferences()

    def loadDefault(self):
        self.preferences = UnitPreferences()
        self.preferences.setProperties({'m':'in', 'm/s':'ft/s', 'N':'N', 'Ns':'Ns', 'Pa':'psi', 'kg':'lb', 'kg/m^3':'lb/in^3'})
