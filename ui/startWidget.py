import sys
from serial.tools.list_ports import comports
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from lib.converter import Converter

from ui.views.StartWidget_ui import Ui_StartWidget

class StartWidget(QWidget):

    beginSetup = pyqtSignal(str, object)
    recvResults = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_StartWidget()
        self.ui.setupUi(self)
        self.setupPortSelector()

        self.ui.pushButtonSetup.pressed.connect(self.setupButtonPressed)
        self.ui.pushButtonResults.pressed.connect(self.recvResultsButtonPressed)

    def getConverter(self):
        return Converter(130000, 0.00079836, 500000, 0.2925)

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
