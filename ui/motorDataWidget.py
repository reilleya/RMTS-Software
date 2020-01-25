import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from ui.views.MotorDataWidget_ui import Ui_MotorDataWidget
from lib.motor import MotorConfig

class MotorDataWidget(QWidget):

    nextPage = pyqtSignal(object)
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MotorDataWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonNext.pressed.connect(self.nextPressed)
        self.ui.pushButtonBack.pressed.connect(self.back.emit)

    def setup(self):
        self.ui.motorData.setPreferences(QApplication.instance().getPreferences())
        self.ui.motorData.loadProperties(MotorConfig())

    def nextPressed(self):
        motorData = MotorConfig()
        motorData.setProperties(self.ui.motorData.getProperties())
        # Validate motor data object
        self.nextPage.emit(motorData)
