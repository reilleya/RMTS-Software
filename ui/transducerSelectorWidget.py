import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from serial.tools.list_ports import comports

from ui.views.TransducerSelectorWidget_ui import Ui_TransducerSelectorWidget
from lib.firing import MotorConfig

class TransducerSelectorWidget(QWidget):

    nextPage = pyqtSignal(object)
    back = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.ui = Ui_TransducerSelectorWidget()
        self.ui.setupUi(self)


    def refreshPorts(self):
        self.ui.comboBoxPort.clear()
        for port in comports():
            self.ui.comboBoxPort.addItem(port.device)

    def getPort(self):
        return self.ui.comboBoxPort.getText()
