import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from ui.views.MotorDataWidget_ui import Ui_MotorDataWidget
from lib.motor import MotorConfig, processRawData

class MotorDataWidget(QWidget):

    nextPage = pyqtSignal()
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MotorDataWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonNext.pressed.connect(self.nextPressed)
        self.ui.pushButtonBack.pressed.connect(self.back.emit)

    def setup(self, data):
        self.raw = {'time': [], 'force': [], 'pressure': []}
        data = data.split('\n')
        for datapoint in data:
            if datapoint == '0,0,0':
                break
            parts = datapoint.split(',')
            self.raw['time'].append(float(parts[0]))
            self.raw['force'].append(float(parts[1]))
            self.raw['pressure'].append(float(parts[2]))
        self.ui.widgetTransducerSelector.reset()
        self.ui.motorData.setPreferences(QApplication.instance().getPreferences())
        self.ui.motorData.loadProperties(MotorConfig())

    def nextPressed(self):
        # Validate motor data object
        motorData = MotorConfig()
        motorData.setProperties(self.ui.motorData.getProperties())
        forceConv, pressConv = self.ui.widgetTransducerSelector.getConverters()
        motor = processRawData(self.raw, forceConv, pressConv, motorData)
        QApplication.instance().newResult(motor)
        self.nextPage.emit()
