import os

from PyQt6.QtWidgets import QWidget, QApplication, QFileDialog, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from lib.logger import logger
from lib.characterization import Characterization
from lib.oMExport import getOpenMotorFileString

from pyFormGen.properties import StringProperty, FloatProperty

from ui.views.CharacterizationWidget_ui import Ui_CharacterizationWidget
from .formDialog import FormDialog

class CharacterizationWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_CharacterizationWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonBack.pressed.connect(self.backPressed)
        self.ui.pushButtonExport.pressed.connect(self.exportPressed)
        self.ui.pushButtonLoadFire.pressed.connect(self.loadPressed)
        self.ui.pushButtonSetAllWebs.pressed.connect(self.setAllWebsPressed)
        self.ui.pushButtonRemove.pressed.connect(self.removePressed)
        self.ui.tableWidgetFirings.cellChanged.connect(self.cellChanged)

        self.app = QApplication.instance()

        header = self.ui.tableWidgetFirings.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.reset()

    def reset(self):
        self.ui.tableWidgetFirings.horizontalHeaderItem(2).setText('Average Pressure ({})'.format(self.app.getUserUnit('Pa')))
        self.ui.tableWidgetFirings.horizontalHeaderItem(3).setText('C* ({})'.format(self.app.getUserUnit('m/s')))
        self.ui.tableWidgetFirings.horizontalHeaderItem(4).setText('Web ({})'.format(self.app.getUserUnit('m')))

        self.isFillingTable = False
        self.ui.tableWidgetFirings.setRowCount(0)

        self.resetResults()

        self.ui.characterizationGraphWidget.clear()
        self.ui.characterizationGraphWidget.clearLine()

        self.characterization = Characterization()

        self.characterization.firingListUpdated.connect(self.firingListUpdated)
        self.characterization.characterizationPointsUpdated.connect(self.characterizationPointsUpdated)
        self.characterization.characterizationResultCalculated.connect(self.newCharacterizationResult)

        self.setWebDialog = None
        self.exportDialog = None

    def resetResults(self):
        self.ui.lineEditCoefficient.setText('-')
        self.ui.lineEditExponent.setText('-')
        self.ui.lineEditCStar.setText('-')
        self.ui.lineEditCStarStdDev.setText('-')

        self.lastResult = None
        self.ui.pushButtonExport.setEnabled(False)

    def loadPressed(self):
        paths = QFileDialog.getOpenFileNames(None, 'Load FIRE', '', 'Firing Data File (*.fire)')[0]
        if paths is not None:
            exceptions = []
            for path in paths:
                try:
                    self.characterization.loadFireFile(path)
                except Exception as e:
                    exceptions.append((os.path.basename(path), str(e)))
            if len(exceptions) > 0:
                message = 'Unable to load all firing files...\n'
                for exception in exceptions:
                    message += '\n{}: {}'.format(*exception)
                self.app.outputMessage(message)

    def setAllWebsPressed(self):
        self.setWebDialog = FormDialog('Set All Webs',
            'Enter a web distance and press apply to set it for all firings.',
            {'web': FloatProperty('Web', 'm', 0, 1)}
        )
        self.setWebDialog.submitted.connect(lambda properties: self.characterization.setAllWebs(properties['web']))
        self.setWebDialog.show()

    def removePressed(self):
        indicies = self.ui.tableWidgetFirings.selectionModel().selectedIndexes()
        if len(indicies) == 0:
            return
        self.characterization.removeFiring(indicies[0].row())

    def backPressed(self):
        if not self.exitCheck():
            return
        self.reset()
        self.back.emit()

    def exitCheck(self):
        if not self.characterization.inProgress():
            return True
        logger.log('Checking if user really wants to exit characterization widget')
        msg = QMessageBox()
        msg.setText("Would you like to discard your in-progress characterization?")
        msg.setWindowTitle("Discard Characterization?")
        msg.setWindowIcon(self.app.icon)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        res = msg.exec()
        if res == QMessageBox.StandardButton.Yes:
            logger.log('User chose to close')
            return True
        if res == QMessageBox.StandardButton.No:
            logger.log('User chose to stay on page')
            return False
        return False

    def firingListUpdated(self, firings):
        self.ui.tableWidgetFirings.setRowCount(0)
        self.ui.tableWidgetFirings.setRowCount(len(firings))

        self.isFillingTable = True
        for row, firing in enumerate(firings):
            cellValues = [
                os.path.basename(firing.path),
                str(round(firing.burnTime, 3)),
                str(round(self.app.convertToUserUnits(firing.averagePressure, 'Pa'), 3)),
                str(round(self.app.convertToUserUnits(firing.cstar, 'm/s'), 3))
            ]
            for col, value in enumerate(cellValues):
                tableWidgetItem = QTableWidgetItem(value)
                tableWidgetItem.setFlags(tableWidgetItem.flags() & ~Qt.ItemFlag.ItemIsEditable)
                tableWidgetItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.tableWidgetFirings.setItem(row, col, tableWidgetItem)
            try:
                conv = str(round(self.app.convertToUserUnits(firing.web, 'm'), 6))
            except TypeError:
                conv = '-'
            tableWidgetItem = QTableWidgetItem(conv)
            tableWidgetItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.tableWidgetFirings.setItem(row, 4, tableWidgetItem)
        self.isFillingTable = False

    def cellChanged(self, row, col):
        if not self.isFillingTable:
            value = self.ui.tableWidgetFirings.item(row, col).text()
            try:
                conv = QApplication.instance().convertFromUserUnits(float(value), 'm')
                self.characterization.updateFiringWeb(row, conv)
            except ValueError:
                logger.log('Invalid value "{}" entered to cell ({}, {})'.format(value, row, col))
        self.ui.tableWidgetFirings.clearSelection()

    def characterizationPointsUpdated(self, points):
        self.ui.characterizationGraphWidget.plotPoints(points)

        # Reset these in case the points don't generate a valid characterization. If they do, they'll be set back in `newCharacterizationResult`
        self.resetResults()

    def newCharacterizationResult(self, result):
        logger.log('A={} m/(s*Pa^n), N={}, R={}, C*={} m/s, C* StdDev={} m/s'.format(result.a, result.n, result.r, result.cstar, result.cstarStdDev))

        burnRateCoeffUnit = self.app.getBurnRateCoefficientUnitString()
        convA = self.app.convertBurnRateCoefficientToUserUnits(result.a, result.n)

        self.ui.lineEditCoefficient.setText('{:.4} {}'.format(convA, burnRateCoeffUnit))
        self.ui.lineEditExponent.setText('{:.4}'.format(result.n))
        self.ui.lineEditCStar.setText(self.app.convertToUserAndFormat(result.cstar, 'm/s', 3))
        self.ui.lineEditCStarStdDev.setText(self.app.convertToUserAndFormat(result.cstarStdDev, 'm/s', 3))

        self.ui.characterizationGraphWidget.displayStats(result.a, result.n, result.r)
        self.ui.characterizationGraphWidget.plotFit(result.a, result.n)

        self.lastResult = result
        self.ui.pushButtonExport.setEnabled(True)

    def exportPressed(self):
        if self.lastResult is None:
            logger.warn('Pressed "export" without results!')
            return

        convA = self.app.convertBurnRateCoefficientToUserUnits(self.lastResult.a, self.lastResult.n)
        burnRateCoeffUnit = self.app.getBurnRateCoefficientUnitString()
        cstarUnit = self.app.getUserUnit('m/s')
        cstar = self.app.convertToUserAndFormat(self.lastResult.cstar, 'm/s', 3)

        self.exportDialog = FormDialog('Export openMotor File',
            'To export an openMotor file containing the calculated propellant properties, edit the values below and press "Apply". Combustion temperature, specific heat ratio, and exhaust molar mass will be estimated from measured characteristic velocity.\n\nCalculated:\nBurn Rate Coefficient (a): {:.4f} {}\nBurn Rate Exponent (n): {:.4f}\nCharacteristic Velocity (C*): {}'.format(convA, burnRateCoeffUnit, self.lastResult.n, cstar),
            {
                'name': StringProperty('Propellant Name'),
                'density': FloatProperty('Density', 'kg/m^3', 1, 10000),
                'minPressure': FloatProperty('Minimum Model Pressure', 'Pa', 0, 7e7),
                'maxPressure': FloatProperty('Maximum Model Pressure', 'Pa', 0, 7e7),
            },
            {
                'minPressure': self.lastResult.minPressure,
                'maxPressure': self.lastResult.maxPressure
            }
        )
        self.exportDialog.submitted.connect(self.exportResult)
        self.exportDialog.show()

    def exportResult(self, form):
        if len(form['name']) == 0:
            self.app.outputMessage('Name must be specified to output propellant.')
            return

        if form['minPressure'] >= form['maxPressure']:
            self.app.outputMessage('Minimum pressure must be less than maximum pressure.')
            return

        path = QFileDialog.getSaveFileName(None, 'Save .ric', '', 'Motor File (*.ric)')[0]
        if path is None or path == '':
            return
        if not path.endswith('.ric'):
            path += '.ric'
        logger.log('Saving motor file to {}'.format(path))
        try:
            molarMass = 23.67
            k = 1.2
            temperature = (self.lastResult.cstar ** 2) * k * ((2 / (k + 1))**((k + 1) / (k - 1))) / 8314.462618 * molarMass

            output = getOpenMotorFileString(
                form['name'],
                form['density'],
                self.lastResult.a,
                self.lastResult.n,
                form['maxPressure'],
                form['minPressure'],
                k,
                molarMass,
                temperature
            )

            with open(path, 'w') as outputFile:
                outputFile.write(output)

        except Exception as err:
            logger.log('Failed to save motor data, err: {}'.format(repr(err)))
            QApplication.instance().outputException(err, 'Error saving file:')
