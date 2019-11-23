from PyQt5.QtCore import QObject, pyqtSignal

from lib.converter import Converter

class SensorProfileManager(QObject):

    profilesChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.profiles = {}

    def loadProfiles(self):
        self.profiles = {'1MT/1600PSI': Converter(105000, 0.00117669, 500000, 0.2925)}
        self.profilesChanged.emit()

    def getProfile(self, name):
        return self.profiles[name]

    def getProfileNames(self):
        return self.profiles.keys()
