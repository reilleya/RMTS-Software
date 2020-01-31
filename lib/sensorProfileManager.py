from PyQt5.QtCore import QObject, pyqtSignal
import yaml

from lib.converter import ConverterType, Converter

class SensorProfileManager(QObject):

    profilesChanged = pyqtSignal()
    profilesPath = 'transducers.yaml'

    def __init__(self):
        super().__init__()
        self.profiles = {}

    def loadProfiles(self):
        try:
            with open(self.profilesPath, 'r') as readLocation:
                fileData = yaml.load(readLocation)
                self.profiles = {name: Converter.fromDictionary(fileData[name]) for name in fileData}
                self.profilesChanged.emit()
        except Exception as err:
            print('Could not read sensor profiles, using default. Error: ' + str(err))
            self.savePreferences()

        self.saveProfiles()
        self.profilesChanged.emit()

    def saveProfiles(self):
        with open(self.profilesPath, 'w') as saveLocation:
            yaml.dump({name:self.profiles[name].toDictionary() for name in self.profiles}, saveLocation)

    def getProfile(self, name):
        return self.profiles[name]

    def getProfileNames(self, filterType=None):
        if filterType is None:
            return self.profiles.keys()
        return filter(lambda name: self.profiles[name].transducer == filterType, self.profiles.keys())
