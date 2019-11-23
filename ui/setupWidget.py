import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from ui.views.SetupWidget_ui import Ui_SetupWidget
from lib.firing import FiringConfig

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

        self.buff = []

        self.ui.pushButtonCalibrate.pressed.connect(self.calibrate.emit)

    def setup(self, converter):
        self.converter = converter

    def processSetupPacket(self, packet):
        if self.converter is None:
            return
        self.buff.append(packet.force)
        if len(self.buff) > 5:
            self.buff.pop(0)
        realForce = round(self.converter.convertForce(sum(self.buff) / len(self.buff)), 1)
        realPressure = round(self.converter.convertPressure(packet.pressure), 1)
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
