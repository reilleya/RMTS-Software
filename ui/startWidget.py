import sys
import yaml
import binascii

from serial.tools.list_ports import comports
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtSvg
from pyFileIO import fileIO

from lib.converter import Converter
from lib.logger import logger
from lib.motor import processRawData, FiringConfig
from lib.fileTypes import FILE_TYPES

from ui.views.StartWidget_ui import Ui_StartWidget

class StartWidget(QWidget):

    beginSetup = pyqtSignal()
    recvResults = pyqtSignal()
    calibrate = pyqtSignal()

    showRawData = pyqtSignal(bytes)
    showResultsPage = pyqtSignal()

    editPreferences = pyqtSignal()
    editTransducer = pyqtSignal()

    showAbout = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_StartWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonSetup.pressed.connect(self.beginSetup.emit)
        self.ui.pushButtonRecvResults.pressed.connect(self.recvResults.emit)
        self.ui.pushButtonCalibrate.pressed.connect(self.calibrate.emit)

        self.ui.pushButtonRawData.pressed.connect(self.processRawData)
        self.ui.pushButtonSavedData.pressed.connect(self.showSavedResultsPressed)
        #self.ui.pushButtonCharacterize.pressed.connect()

        self.ui.pushButtonPreferences.pressed.connect(self.editPreferences.emit)
        self.ui.pushButtonEditTransducer.pressed.connect(self.editTransducer.emit)
        self.ui.pushButtonAbout.pressed.connect(self.showAbout.emit)

        logo = QtSvg.QSvgWidget()
        self.ui.groupBoxLogo.setLayout(QVBoxLayout())
        self.ui.groupBoxLogo.layout().addWidget(logo)
        logo.load('resources/logo_large.svg')

    def showSavedResultsPressed(self):
        path = QFileDialog.getOpenFileName(None, 'Load FIRE', '', 'Firing Data File (*.fire)')[0]
        if path != '':
            try:
                data = fileIO.load(FILE_TYPES.FIRING, path)
            except Exception as err:
                logger.log('Failed to load firing, err: {}'.format(repr(err)))
                return
            try:
                motor = processRawData(data['rawData'],
                        Converter(data['forceConv']),
                        Converter(data['pressureConv']),
                        FiringConfig(data['motorInfo'])
                    )
            except Exception as err:
                logger.log('Failed to process firing, err: {}'.format(repr(err)))
                return
            QApplication.instance().newResult(motor)
            self.showResultsPage.emit()

    def processRawData(self):
        path = QFileDialog.getOpenFileName(None, 'Load Raw Data', '', 'Raw Firing Data File (*.LOG)')[0]
        if path != '':
            with open(path, 'rb') as fileData:
                self.showRawData.emit(binascii.hexlify(fileData.read()))
