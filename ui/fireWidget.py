import sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from ui.views.FireWidget_ui import Ui_FireWidget

class FireWidget(QWidget):

    setup = pyqtSignal()
    fire = pyqtSignal()
    stop = pyqtSignal()
    results = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_FireWidget()
        self.ui.setupUi(self)

        self.ui.lineEditArm.textChanged.connect(self.armBoxTextChanged)
        self.ui.lineEditStop.textChanged.connect(self.stopBoxTextChanged)
        self.ui.pushButtonFire.pressed.connect(self.fireButtonPressed)
        self.ui.pushButtonStop.pressed.connect(self.stop.emit)
        self.ui.pushButtonSetup.pressed.connect(self.setupButtonPressed)
        self.ui.pushButtonResults.pressed.connect(self.results.emit)

    def reset(self):
        self.ui.pushButtonStop.setEnabled(False)
        self.ui.pushButtonFire.setEnabled(False)
        self.ui.pushButtonResults.setEnabled(True)

    def setupButtonPressed(self):
        self.reset()
        self.setup.emit()

    def armBoxTextChanged(self):
        self.ui.pushButtonFire.setEnabled(self.ui.lineEditArm.text() == "ARM")

    def stopBoxTextChanged(self):
        self.ui.pushButtonStop.setEnabled(self.ui.lineEditStop.text() == "STOP")

    def fireButtonPressed(self):
        self.ui.pushButtonResults.setEnabled(True)
        self.fire.emit()
