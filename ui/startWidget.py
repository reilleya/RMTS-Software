import sys
import yaml
from serial.tools.list_ports import comports
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from PyQt5.QtCore import pyqtSignal

from lib.converter import Converter

from ui.views.StartWidget_ui import Ui_StartWidget

class StartWidget(QWidget):

    beginSetup = pyqtSignal()
    recvResults = pyqtSignal()
    editPreferences = pyqtSignal()
    calibrate = pyqtSignal()
    editTransducer = pyqtSignal()
    showFireFile = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_StartWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonSetup.pressed.connect(self.beginSetup.emit)
        #self.ui.pushButtonResults.pressed.connect(self.recvResultsButtonPressed)
        self.ui.pushButtonPreferences.pressed.connect(self.editPreferences.emit)
        self.ui.pushButtonSavedData.pressed.connect(self.showSavedResultsPressed)
        self.ui.pushButtonCalibrate.pressed.connect(self.calibrate.emit)
        self.ui.pushButtonEditTransducer.pressed.connect(self.editTransducer.emit)

    def setup(self):
        self.setupPortSelector()
        self.ui.comboBoxProfile.clear()
        self.ui.comboBoxProfile.addItems(QApplication.instance().sensorProfileManager.getProfileNames())

    def showSavedResultsPressed(self):
        path = QFileDialog.getOpenFileName(None, 'Load FIRE', '', 'Firing Data File (*.fire)')[0]
        if path != '':
            with open(path, 'r') as fileData:
                data = yaml.load(fileData)
                self.showFireFile.emit(data)
