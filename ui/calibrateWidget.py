import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from lib.calibration import Calibration

from ui.views.CalibrateWidget_ui import Ui_CalibrateWidget

class CalibrateWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_CalibrateWidget()
        self.ui.setupUi(self)

        self.calibrationRun = None

        self.ui.pushButtonBack.pressed.connect(self.backPressed)
        self.ui.pushButtonConnect.pressed.connect(self.connectPressed)

    def reset(self):
        self.ui.lineEditLoadCell.setText("")
        self.ui.lineEditPressureTransducer.setText("")

    def backPressed(self):
        self.exit()
        self.calibrationRun = None
        self.reset()
        self.back.emit()

    def connectPressed(self):
        port = self.ui.widgetPortSelector.getPort()
        self.calibrationRun = Calibration(port)
        self.calibrationRun.newLoadCellReading.connect(self.updateLoadCellOutput)
        self.calibrationRun.newPressureTransducerReading.connect(self.updatePressureTransducerOutput)

    def updateLoadCellOutput(self, value):
        self.ui.lineEditLoadCell.setText(str(int(value)))

    def updatePressureTransducerOutput(self, value):
        self.ui.lineEditPressureTransducer.setText(str(int(value)))

    def exit(self):
        if self.calibrationRun is not None:
            self.calibrationRun.exit()
