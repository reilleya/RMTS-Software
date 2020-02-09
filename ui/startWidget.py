import sys
import yaml
from serial.tools.list_ports import comports
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from PyQt5.QtCore import pyqtSignal

from lib.converter import Converter
from lib.motor import processRawData, FiringConfig

from ui.views.StartWidget_ui import Ui_StartWidget

class StartWidget(QWidget):

    beginSetup = pyqtSignal()
    recvResults = pyqtSignal()
    calibrate = pyqtSignal()

    showRawData = pyqtSignal(str)
    showResultsPage = pyqtSignal()

    editPreferences = pyqtSignal()
    editTransducer = pyqtSignal()

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
        #self.ui.pushButtonAbout.pressed.connect()

    def showSavedResultsPressed(self):
        path = QFileDialog.getOpenFileName(None, 'Load FIRE', '', 'Firing Data File (*.fire)')[0]
        if path != '':
            with open(path, 'r') as fileData:
                data = yaml.load(fileData)
                motor = processRawData(data['rawData'],
                    Converter(data['forceConv']),
                    Converter(data['pressureConv']),
                    FiringConfig(data['motorInfo'])
                )
                QApplication.instance().newResult(motor)
                self.showResultsPage.emit()

    def processRawData(self):
        path = QFileDialog.getOpenFileName(None, 'Load Raw Data', '', 'Raw Firing Data File (*.TXT)')[0]
        if path != '':
            with open(path, 'r') as fileData:
                self.showRawData.emit(fileData.read())
