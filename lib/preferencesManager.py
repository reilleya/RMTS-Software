from PyQt5.QtCore import QObject, pyqtSignal
import yaml

from pyFormGen.unitPreferences import UnitPreferences
from pyFormGen.collectionEditor import CollectionEditor

class PreferencesManager(QObject):

    preferencesChanged = pyqtSignal()
    preferencesPath = 'preferences.yaml'

    def __init__(self):
        super().__init__()
        self.preferences = UnitPreferences()

    def loadPreferences(self):
        try:
            with open(self.preferencesPath, 'r') as readLocation:
                fileData = yaml.load(readLocation) 
                self.preferences.setProperties(fileData)
                self.preferencesChanged.emit()
        except Exception as err:
            print('Could not read preferences, using default. Error: ' + str(err))
            self.loadDefault()
            self.savePreferences()

    def savePreferences(self):
        with open(self.preferencesPath, 'w') as saveLocation:
            yaml.dump(self.preferences.getProperties(), saveLocation)

    def setPreferences(self, pref):
        self.preferences = pref
        self.preferencesChanged.emit()
        self.savePreferences()

    def loadDefault(self):
        self.preferences = UnitPreferences()
        self.preferences.setProperties({'m':'in', 'm/s':'ft/s', 'N':'N', 'Ns':'Ns', 'Pa':'psi', 'kg': 'lb', 'kg/m^3':'lb/in^3'})
