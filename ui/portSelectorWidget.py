from PyQt5.QtWidgets import QWidget
from serial.tools.list_ports import comports

from ui.views.PortSelectorWidget_ui import Ui_PortSelectorWidget

class PortSelectorWidget(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.ui = Ui_PortSelectorWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonRefresh.pressed.connect(self.refreshPorts)
        self.refreshPorts()

    def refreshPorts(self):
        self.ui.comboBoxPort.clear()
        for port in comports():
            self.ui.comboBoxPort.addItem(port.device)

    def getPort(self):
        return self.ui.comboBoxPort.currentText()
