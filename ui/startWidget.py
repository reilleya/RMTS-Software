import sys
from serial.tools.list_ports import comports
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from ui.views.StartWidget_ui import Ui_StartWidget

class StartWidget(QWidget):

    beginSetup = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ui = Ui_StartWidget()
        self.ui.setupUi(self)
        self.setupPortSelector()

        self.ui.pushButtonSetup.pressed.connect(self.setupButtonPressed)


    def setupPortSelector(self):
        for port in comports():
            self.ui.comboBoxPort.addItem(port.device)

    def setupButtonPressed(self):
        port = self.ui.comboBoxPort.currentText()
        # Validate entries
        self.beginSetup.emit(port)
