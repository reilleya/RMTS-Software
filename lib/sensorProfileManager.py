from PyQt5.QtCore import QObject, pyqtSignal

from lib.converter import ConverterType, Converter

class SensorProfileManager(QObject):

    profilesChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.profiles = {}

    def loadProfiles(self):
        self.profiles = {
            '1 MT': Converter(ConverterType.LOAD_CELL, -129.125946, 0.001196223066),
            '1600 PSI #1': Converter(ConverterType.PRESSURE_TRANSDUCER, -1255025.164, 1.645964884),
            '1600 PSI #2': Converter(ConverterType.PRESSURE_TRANSDUCER, -1255025.164, 1.65)
        }
        self.profilesChanged.emit()

    def getProfile(self, name):
        return self.profiles[name]

    def getProfileNames(self, filterType=None):
        if filterType is None:
            return self.profiles.keys()
        return filter(lambda name: self.profiles[name].transducer == filterType, self.profiles.keys())
