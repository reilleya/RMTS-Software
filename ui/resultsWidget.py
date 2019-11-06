import sys
from PyQt5.QtWidgets import QWidget

from ui.views.ResultsWidget_ui import Ui_ResultsWidget

from lib.firing import Firing

class ResultsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)

        self.firing = None

        self.reset()

    def processResultsPacket(self, packet):
        if self.firing is not None: 
            self.firing.addDatapoint(packet)

    def onFireButtonPressed(self):
        fireData = self.ui.widgetFiringConfig.getProperties()
        # Validate fire object
        self.beginFire.emit(fireData)

    def reset(self):
        self.firing = Firing()
        self.firing.newGraph.connect(self.showResults)

    def showResults(self, motorData):
        self.ui.labelMotorDesignation.setText(motorData.getMotorDesignation())
        self.ui.labelBurnTime.setText("{} s".format(round(motorData.getBurnTime(), 3)))
        self.ui.labelStartupTime.setText("{} s".format(round(motorData.getStartupTime(), 3)))

        self.ui.labelImpulse.setText("{} Ns".format(round(motorData.getImpulse(), 1)))
        self.ui.labelPropellantMass.setText("{} Kg".format(round(motorData.getPropMass(), 3)))
        self.ui.labelISP.setText("{} s".format(round(motorData.getISP(), 3)))

        self.ui.labelPeakThrust.setText("{} N".format(round(motorData.getPeakThrust(), 1)))
        self.ui.labelAverageThrust.setText("{} N".format(round(motorData.getAverageThrust(), 1)))

        self.ui.widgetGraph.plotData(motorData.getTime(), motorData.getForce())
