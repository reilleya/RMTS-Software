import sys
import yaml
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from PyQt5.QtCore import pyqtSignal

from ui.views.ResultsWidget_ui import Ui_ResultsWidget
from .engExporterWidget import engExportWidget

from lib.firing import Firing

class ResultsWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)

        self.motorData = None

        self.engExporter = engExportWidget()
        self.engExporter.newData.connect(self.exportENG)

        self.ui.checkBoxForce.stateChanged.connect(self.regraphData)
        self.ui.checkBoxPressure.stateChanged.connect(self.regraphData)
        self.ui.checkBoxGridLines.stateChanged.connect(self.regraphData)
        self.ui.radioButtonTranslated.toggled.connect(self.regraphData)
        self.ui.radioButtonRaw.toggled.connect(self.regraphData)

        self.ui.pushButtonFIRE.pressed.connect(self.saveFIRE)
        self.ui.pushButtonENG.pressed.connect(self.saveENG)
        self.ui.pushButtonCSV.pressed.connect(self.saveCSV)

        self.ui.pushButtonBack.pressed.connect(self.back.emit) # Todo: confirm they have saved and clear firing and plot

        self.resultsFields = [
            self.ui.labelMotorDesignation, self.ui.labelBurnTime, self.ui.labelStartupTime,
            self.ui.labelImpulse, self.ui.labelPropellantMass, self.ui.labelISP,
            self.ui.labelPeakThrust, self.ui.labelAverageThrust, self.ui.labelDatapoints,
            self.ui.labelPeakPressure, self.ui.labelAveragePressure, self.ui.labelCStar
        ]

    def reset(self):
        self.motorData = None
        self.ui.widgetGraph.clear()
        for field in self.resultsFields:
            field.setText('-')

    def regraphData(self):
        force = None
        pressure = None
        grid = self.ui.checkBoxGridLines.isChecked()
        if self.ui.radioButtonTranslated.isChecked():
            if self.motorData is None:
                return
            if self.ui.checkBoxForce.isChecked():
                force = self.motorData.getForce()
            if self.ui.checkBoxPressure.isChecked():
                pressure = self.motorData.getPressure()
            self.ui.widgetGraph.convertAndPlot(self.motorData.getTime(), force=force, pressure=pressure, gridLines=grid)
        else:
            if self.ui.checkBoxForce.isChecked():
                force = self.motorData.getRawForce()
            if self.ui.checkBoxPressure.isChecked():
                pressure = self.motorData.getRawPressure()
            self.ui.widgetGraph.plotData(self.motorData.getRawTime(), force=force, pressure=pressure, gridLines=grid)

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

    def saveFIRE(self):
        path = QFileDialog.getSaveFileName(None, 'Save FIRE', '', 'Firing Data File (*.fire)')[0]
        if path is not None:
            if not path.endswith('.fire'):
                path += '.fire'
            with open(path, 'w') as outFile:
                yaml.dump(self.motorData.toDictionary(), outFile)

    def saveCSV(self):
        path = QFileDialog.getSaveFileName(None, 'Save CSV', '', 'Comma Separated Values (*.csv)')[0]
        if path is not None:
            if not path.endswith('.csv'):
                path += '.csv'
            data = self.motorData.getCSV()
            with open(path, 'w') as outFile:
                outFile.write(data)

    def saveENG(self):
        self.engExporter.show()

    def exportENG(self, config):
        title = 'Save ENG'
        formats = 'RASP ENG File (*.eng)'
        if config['append'] == 'Append':
            mode = 'a'
            path = QFileDialog.getSaveFileName(None, title, '', formats, options=QFileDialog.DontConfirmOverwrite)[0]
        else:
            mode = 'w'
            path = QFileDialog.getSaveFileName(None, title, '', formats)[0]
        if path is not None:
            if not path.endswith('.eng'):
                path += '.eng'
            with open(path, mode) as outFile:
                propMass = self.motorData.getPropMass()
                contents = ' '.join([config['designation'],
                                     str(round(config['diameter'] * 1000, 6)),
                                     str(round(config['length'] * 1000, 6)),
                                     'P',
                                     str(round(propMass, 6)),
                                     str(round(propMass + self.motorData.getHardwareMass(), 6)),
                                     config['manufacturer']
                                     ]) + '\n'

                timeData = self.motorData.getTime()
                forceData = self.motorData.getForce()
                # Add on a 0-thrust datapoint right after the burn to satisfy RAS Aero
                if forceData[-1] != 0:
                    timeData.append(timeData[-1] + 0.01)
                    forceData.append(0)
                for time, force in zip(timeData, forceData):
                    if time == 0 and force == 0: # Increase the first point so it isn't 0 thrust
                        force += 0.01
                    contents += str(round(time, 4)) + ' ' + str(round(force, 4)) + '\n'

                contents += ';\n;\n'

                outFile.write(contents)
