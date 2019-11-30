import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from ui.views.SetupWidget_ui import Ui_SetupWidget
from lib.firing import FiringConfig

class LowPass():
    def __init__(self, historyLength):
        self.maxSize = historyLength
        self._buffer = []

    def addData(self, data):
        self._buffer.append(data)
        if len(self._buffer) > self.maxSize:
            self._buffer.pop(0)
        return sum(self._buffer) / len(self._buffer)

class SetupWidget(QWidget):

    gotoFirePage = pyqtSignal()
    newFiringConfig = pyqtSignal(object)

    calibrate = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_SetupWidget()
        self.ui.setupUi(self)

        self.converter = None
        self.ui.pushButtonFire.pressed.connect(self.onFireButtonPressed)
        self.ui.widgetFiringConfig.loadProperties(FiringConfig())

        self.forceBuff = LowPass(5)
        self.pressureBuff = LowPass(5)

        self.ui.pushButtonCalibrate.pressed.connect(self.calibrate.emit)

    def setup(self, converter):
        self.converter = converter

    def processSetupPacket(self, packet):
        if self.converter is None:
            return

        realForce = round(self.converter.convertForce(self.forceBuff.addData(packet.force)), 1)
        realPressure = round(self.converter.convertPressure(self.pressureBuff.addData(packet.pressure)), 1)
        hasContinuity = "Yes" if packet.continuity else "No"
        self.ui.lineEditForce.setText("{} N".format(realForce))
        self.ui.lineEditPressure.setText("{} Pa".format(realPressure))
        self.ui.lineEditContinuity.setText(hasContinuity)

    def onFireButtonPressed(self):
        fireData = FiringConfig()
        fireData.setProperties(self.ui.widgetFiringConfig.getProperties())
        # Validate fire object
        self.newFiringConfig.emit(fireData)
        self.gotoFirePage.emit()
