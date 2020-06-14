import sys
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal

from pyFileIO import fileIO
from ui.views.ResultsWidget_ui import Ui_ResultsWidget
from .engExporterWidget import engExportWidget

from lib.firing import Firing
from lib.logger import logger
from lib.fileTypes import FILE_TYPES
from lib.datasheet import saveDatasheet

class ResultsWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)

        self.motorData = None
        self.liveMode = False
        self.saved = False

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
        self.ui.pushButtonRawCSV.pressed.connect(self.saveRawCSV)
        self.ui.pushButtonDatasheet.pressed.connect(self.saveDatasheet)

        self.ui.pushButtonBack.pressed.connect(self.backPressed)

        self.resultsFields = [
            self.ui.labelMotorDesignation, self.ui.labelBurnTime, self.ui.labelStartupTime,
            self.ui.labelImpulse, self.ui.labelPropellantMass, self.ui.labelISP,
            self.ui.labelPeakThrust, self.ui.labelAverageThrust, self.ui.labelThrustCoefficient,
            self.ui.labelPeakPressure, self.ui.labelAveragePressure, self.ui.labelCStar
        ]

        self.reset()

    def reset(self):
        self.motorData = None
        self.ui.widgetGraph.clear()
        for field in self.resultsFields:
            field.setText('-')
        self.liveMode = False
        self.saved = False
        self.ui.groupBoxRecvResults.setVisible(False)
        self.ui.widgetDataAge.reset(False)

    def setupLive(self, firingLength):
        logger.log('Set up results view for live receiving. Max size: {}'.format(firingLength))
        self.liveMode = True
        self.ui.groupBoxRecvResults.setVisible(True)
        self.ui.progressBarReceived.setMaximum(firingLength)
        self.ui.progressBarReceived.setValue(0)
        self.ui.widgetDataAge.start()

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
        self.ui.labelBurnTime.setText(app.convertToUserAndFormat(motorData.getBurnTime(), 's', 3))
        self.ui.labelStartupTime.setText(app.convertToUserAndFormat(motorData.getStartupTime(), 's', 3))
        self.ui.labelPropellantMass.setText(app.convertToUserAndFormat(motorData.getPropMass(), 'kg', 3))

        showForce = motorData.hasForceConverter()
        if showForce:
            self.ui.labelMotorDesignation.setText(motorData.getMotorDesignation())
            self.ui.labelImpulse.setText(app.convertToUserAndFormat(motorData.getImpulse(), 'Ns', 1))
            self.ui.labelISP.setText(app.convertToUserAndFormat(motorData.getISP(), 's', 3))
            self.ui.labelPeakThrust.setText(app.convertToUserAndFormat(motorData.getPeakThrust(), 'N', 1))
            self.ui.labelAverageThrust.setText(app.convertToUserAndFormat(motorData.getAverageThrust(), 'N', 1))
        self.ui.checkBoxForce.setChecked(showForce)
        self.ui.checkBoxForce.setEnabled(showForce)
        self.ui.pushButtonENG.setEnabled(showForce)

        showPressure =  motorData.hasPressureConverter()
        if showPressure:
            self.ui.labelPeakPressure.setText(app.convertToUserAndFormat(motorData.getPeakPressure(), 'Pa', 3))
            self.ui.labelAveragePressure.setText(app.convertToUserAndFormat(motorData.getAveragePressure(), 'Pa', 3))
            self.ui.labelCStar.setText(app.convertToUserAndFormat(motorData.getCStar(), 'm/s', 3))
        self.ui.checkBoxPressure.setChecked(showPressure)
        self.ui.checkBoxPressure.setEnabled(showPressure)

        if showForce and showPressure:
            self.ui.labelThrustCoefficient.setText(str(round(motorData.getThrustCoefficient(), 3)))

        if self.liveMode:
            self.ui.progressBarReceived.setValue(len(motorData.getRawTime()))

        self.motorData = motorData
        self.regraphData()

    def newResultsPacket(self):
        self.ui.widgetDataAge.reset()

    def saveFIRE(self):
        path = QFileDialog.getSaveFileName(None, 'Save FIRE', '', 'Firing Data File (*.fire)')[0]
        if path is None or path == '':
            return
        if not path.endswith('.fire'):
            path += '.fire'
        logger.log('Saving firing to {}'.format(path))
        try:
            fileIO.save(FILE_TYPES.FIRING, self.motorData.toDictionary(), path)
            self.saved = True
        except Exception as err:
            logger.log('Failed to save firing data, err: {}'.format(repr(err)))

    def saveCSV(self):
        path = QFileDialog.getSaveFileName(None, 'Save CSV', '', 'Comma Separated Values (*.csv)')[0]
        if path is None or path == '':
            return
        if not path.endswith('.csv'):
            path += '.csv'
        data = self.motorData.getCSV()
        logger.log('Saving CSV to {}'.format(path))
        with open(path, 'w') as outFile:
            outFile.write(data)

    def saveRawCSV(self):
        path = QFileDialog.getSaveFileName(None, 'Save Raw CSV', '', 'Comma Separated Values (*.csv)')[0]
        if path is None or path == '':
            return
        if not path.endswith('.csv'):
            path += '.csv'
        data = self.motorData.getRawCSV()
        logger.log('Saving raw CSV to {}'.format(path))
        with open(path, 'w') as outFile:
            outFile.write(data)

    def saveENG(self):
        logger.log('Showing ENG exporter')
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
        if path is None or path == '':
            return
        if not path.endswith('.eng'):
            path += '.eng'
        logger.log('Saving ENG to {} (Mode={})'.format(path, config['append']))
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

    def saveDatasheet(self):
        path = QFileDialog.getSaveFileName(None, 'Save Motor Datasheet', '',
            'Portable Network Graphic Files (*.png);;Portable Document Format Files (*.pdf)')[0]
        if path is None or path == '':
            return
        if not path.endswith('.png') and not path.endswith('.pdf'):
            path += '.png'
        logger.log('Saving datasheet to "{}"'.format(path))
        app = QApplication.instance()
        saveDatasheet(self.motorData, path, app.convertToUserAndFormat, app.convertAllToUserUnits, app.getUserUnit)

    # Returns true if it is safe to exit
    def unsavedCheck(self):
        if not self.liveMode or self.saved:
            return True
        logger.log('Checking if user wants to save before exiting results widget')
        msg = QMessageBox()
        msg.setText("The received results have not been saved. Close anyway?")
        msg.setWindowTitle("Close without saving?")
        msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        res = msg.exec_()
        if res == QMessageBox.Discard:
            logger.log('User chose to discard results')
            return True
        if res == QMessageBox.Save:
            logger.log('User chose to save first')
            self.saveFIRE()
            return self.saved
        return False

    def backPressed(self):
        if not self.unsavedCheck():
            return
        self.reset()
        self.back.emit()
