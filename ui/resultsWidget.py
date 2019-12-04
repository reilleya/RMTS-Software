import sys
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog

from ui.views.ResultsWidget_ui import Ui_ResultsWidget

from lib.firing import Firing

class ResultsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)

        self.firing = None
        self.motorData = None

        self.ui.checkBoxForce.stateChanged.connect(self.regraphData)
        self.ui.checkBoxPressure.stateChanged.connect(self.regraphData)
        self.ui.radioButtonTranslated.toggled.connect(self.regraphData)
        self.ui.radioButtonRaw.toggled.connect(self.regraphData)

        self.ui.pushButtonCSV.pressed.connect(self.saveCSV)

    def processResultsPacket(self, packet):
        if self.firing is not None: 
            self.firing.addDatapoint(packet)

    def setFiring(self, firing):
        self.firing = firing
        self.firing.newGraph.connect(self.showResults)

    def regraphData(self):
        force = None
        pressure = None
        if self.ui.radioButtonTranslated.isChecked():
            if self.motorData is None:
                return
            if self.ui.checkBoxForce.isChecked():
                force = self.motorData.getForce()
            if self.ui.checkBoxPressure.isChecked():
                pressure = self.motorData.getPressure()
            self.ui.widgetGraph.convertAndPlot(self.motorData.getTime(), force=force, pressure=pressure)
        else:
            if self.ui.checkBoxForce.isChecked():
                force = self.motorData.getRawForce()
            if self.ui.checkBoxPressure.isChecked():
                pressure = self.motorData.getRawPressure()
            self.ui.widgetGraph.plotData(self.motorData.getRawTime(), force=force, pressure=pressure)

    def showResults(self, motorData):
        app = QApplication.instance()
        self.ui.labelMotorDesignation.setText(motorData.getMotorDesignation())
        self.ui.labelBurnTime.setText(app.convertToUserAndFormat(motorData.getBurnTime(), 's', 3))
        self.ui.labelStartupTime.setText(app.convertToUserAndFormat(motorData.getStartupTime(), 's', 3))

        self.ui.labelImpulse.setText(app.convertToUserAndFormat(motorData.getImpulse(), 'Ns', 1))
        self.ui.labelPropellantMass.setText(app.convertToUserAndFormat(motorData.getPropMass(), 'kg', 3))
        self.ui.labelISP.setText(app.convertToUserAndFormat(motorData.getISP(), 's', 3))

        self.ui.labelPeakThrust.setText(app.convertToUserAndFormat(motorData.getPeakThrust(), 'N', 1))
        self.ui.labelAverageThrust.setText(app.convertToUserAndFormat(motorData.getAverageThrust(), 'N', 1))
        self.ui.labelDatapoints.setText(str(motorData.getNumDataPoints()))

        self.ui.labelPeakPressure.setText(app.convertToUserAndFormat(motorData.getPeakPressure(), 'Pa', 3))
        self.ui.labelAveragePressure.setText(app.convertToUserAndFormat(motorData.getAveragePressure(), 'Pa', 3))
        self.ui.labelCStar.setText(app.convertToUserAndFormat(motorData.getCStar(), 'm/s', 3))

        self.motorData = motorData
        self.regraphData()

    def saveCSV(self):
        path = QFileDialog.getSaveFileName(None, 'Save CSV', '', 'Comma Separated Values (*.csv)')[0]
        if path is not None:
            if not path.endswith('.csv'):
                path += '.csv'
            data = self.motorData.getCSV()
            with open(path, 'w') as outFile:
                outFile.write(data)
