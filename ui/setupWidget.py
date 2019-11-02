import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from ui.views.SetupWidget_ui import Ui_SetupWidget

class SetupWidget(QWidget):

    beginFire = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_SetupWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonFire.pressed.connect(self.onFireButtonPressed)

    def processSetupPacket(self, packet):
        realForce = round((packet.force - 110000) * 70 / 390000, 1)
        realPressure = round(((packet.pressure - 829000) / 10000) + 14.7, 1)
        hasContinuity = "Yes" if packet.continuity else "No"
        self.ui.lineEditForce.setText("{} Lbf".format(realForce))
        self.ui.lineEditPressure.setText("{} PSI".format(realPressure))
        self.ui.lineEditContinuity.setText(hasContinuity)

    def onFireButtonPressed(self):
        fireData = {}
        # Validate fire object
        self.beginFire.emit(fireData)
