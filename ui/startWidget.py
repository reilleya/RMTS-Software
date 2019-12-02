import sys
from serial.tools.list_ports import comports
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from lib.converter import Converter

from ui.views.StartWidget_ui import Ui_StartWidget

class StartWidget(QWidget):

    beginSetup = pyqtSignal(str, object)
    recvResults = pyqtSignal(str, object)
    editPreferences = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_StartWidget()
        self.ui.setupUi(self)
        self.setup()

        self.ui.pushButtonSetup.pressed.connect(self.setupButtonPressed)
        self.ui.pushButtonResults.pressed.connect(self.recvResultsButtonPressed)
        self.ui.pushButtonPreferences.pressed.connect(self.editPreferences.emit)

    def setup(self):
        self.setupPortSelector()
        self.ui.comboBoxProfile.clear()
        self.ui.comboBoxProfile.addItems(QApplication.instance().sensorProfileManager.getProfileNames())

    def getConverter(self):
        return QApplication.instance().sensorProfileManager.getProfile(self.ui.comboBoxProfile.currentText())

    def setupPortSelector(self):
        for port in comports():
            self.ui.comboBoxPort.addItem(port.device)

    def setupButtonPressed(self):
        port = self.ui.comboBoxPort.currentText()

        # Validate entries
        self.beginSetup.emit(port, self.getConverter())

    def recvResultsButtonPressed(self):
        port = self.ui.comboBoxPort.currentText()

        self.recvResults.emit(port, self.getConverter())
