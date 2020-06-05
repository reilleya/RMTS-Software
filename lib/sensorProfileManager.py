from PyQt5.QtCore import QObject, pyqtSignal

from pyFileIO import fileIO
from lib.converter import ConverterType, Converter
from .logger import logger
from .fileTypes import FILE_TYPES
import os.path
import shutil

class SensorProfileManager(QObject):

    profilesChanged = pyqtSignal()
    TRANSDUCERS_PATH = 'transducers.yaml'

    def __init__(self):
        super().__init__()
        self.profiles = []

    def loadProfiles(self):
        try:
            transducerData = fileIO.loadFromDataDirectory(FILE_TYPES.TRANSDUCERS, self.TRANSDUCERS_PATH)
            self.profiles = [Converter(properties) for properties in transducerData]
        except Exception as err:
            logger.error('Could not read transducer data, saving empty. Error: {}'.format(repr(err)))
            fromPath = '{}/{}'.format(fileIO.getDataDirectory(), self.TRANSDUCERS_PATH)
            toPath = '{}/{}'.format(fileIO.getDataDirectory(), self.TRANSDUCERS_PATH + '.bak')
            if os.path.isfile(fromPath):
                shutil.move(fromPath, toPath)
            self.saveProfiles()

        self.profilesChanged.emit()

    def saveProfiles(self):
        logger.log('Saving transducer profiles...')
        try:
            transducerData = [profile.getProperties() for profile in self.profiles]
            fileIO.saveToDataDirectory(FILE_TYPES.TRANSDUCERS, transducerData, self.TRANSDUCERS_PATH)
        except Exception as err:
            logger.error('Could not save transducer data. Error: {}'.format(repr(err)))

    def getProfile(self, name):
        for profile in self.profiles:
            if profile.getProperty('name') == name:
                return profile

    def getProfileNames(self, filterType=None):
        if filterType is None:
            return [prof.getProperty('name') for prof in self.profiles]
        return filter(lambda name: self.getProfile(name).getProperty('type') == filterType, self.getProfileNames())

    def addProfile(self, profile):
        logger.log('Adding profile of type "{}" with name "{}"'.format(
            profile.getProperty('type'),
            profile.getProperty('name')
        ))
        self.profiles.append(profile)
        self.saveProfiles()
        self.profilesChanged.emit()
