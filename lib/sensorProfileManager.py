from PyQt5.QtCore import QObject, pyqtSignal

from lib.converter import Converter

class SensorProfileManager(QObject):

    profilesChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.profiles = {}

    def loadProfiles(self):
        self.profiles = {'1MT/1600PSI': Converter(-129.125946, 0.001196223066, -1255025.164, 1.645964884)}
        self.profilesChanged.emit()

    def getProfile(self, name):
        return self.profiles[name]

    def getProfileNames(self):
        return self.profiles.keys()
