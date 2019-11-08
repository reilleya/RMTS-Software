import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from pyFormGen.properties import PropertyCollection, FloatProperty, EnumProperty

from ui.views.SetupWidget_ui import Ui_SetupWidget

class FiringConfig(PropertyCollection):
    def __init__(self):
        super().__init__()
        self.props['recordingDuration'] = FloatProperty('Recording Duration', 's', 5, 20)
        self.props['firingDuration'] = FloatProperty('Fire Duration', 's', 0.25, 3)
        self.props['motorOrientation'] = EnumProperty('Motor Orientation', ['Vertical', 'Horizontal'])
        self.props['propellantMass'] = FloatProperty('Propellant Mass', 'kg', 0.01, 100)
        self.props['throatDiameter'] = FloatProperty('Throat Diameter', 'm', 0.0001, 1)

class SetupWidget(QWidget):

    beginFire = pyqtSignal(dict, object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_SetupWidget()
        self.ui.setupUi(self)

        self.converter = None
        self.ui.pushButtonFire.pressed.connect(self.onFireButtonPressed)
        self.ui.widgetFiringConfig.loadProperties(FiringConfig())

    def setConverter(self, converter):
        self.converter = converter

    def processSetupPacket(self, packet):
        realForce = round(self.converter.convertForce(packet.force), 1)
        realPressure = round(self.converter.convertPressure(packet.pressure), 1)
        hasContinuity = "Yes" if packet.continuity else "No"
        self.ui.lineEditForce.setText("{} N".format(realForce))
        self.ui.lineEditPressure.setText("{} PSI".format(realPressure))
        self.ui.lineEditContinuity.setText(hasContinuity)

    def onFireButtonPressed(self):
        fireData = self.ui.widgetFiringConfig.getProperties()
        # Validate fire object
        self.beginFire.emit(fireData, self.converter)
