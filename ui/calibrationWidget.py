from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt

from lib.logger import logger

from ui.views.CalibrationWidget_ui import Ui_CalibrationWidget

class CalibrationWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_CalibrationWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonBack.pressed.connect(self.backPressed)
        self.ui.pushButtonCapture.pressed.connect(self.capturePressed)
        self.ui.pushButtonRemove.pressed.connect(self.removePressed)
        self.ui.pushButtonSave.pressed.connect(self.savePressed)
        self.ui.tableWidgetPoints.cellChanged.connect(self.cellChanged)

        self.ui.tableWidgetPoints.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);

        self.app = QApplication.instance()

        self.reset()

    def reset(self):
        self.calibration = None
        self.clearing = False
        self.baseUnit = ""
        self.converter = None
        self.ui.tableWidgetPoints.setRowCount(0)
        self.ui.widgetGraph.clear()

    def newCalibration(self, calibration):
        self.ui.pushButtonSave.setEnabled(False)
        self.ui.lineEditCurrentConverted.setText('-')
        self.calibration = calibration
        self.calibration.newReading.connect(self.newRawReading)
        self.calibration.newPoints.connect(self.newPoints)
        self.calibration.newGraphPoints.connect(self.newGraphPoints)
        self.calibration.newRegression.connect(self.newRegression)
        self.calibration.newConverter.connect(self.newConverter)
        self.calibration.newInfo.connect(self.newInfo)

    def newRawReading(self, value):
        self.ui.lineEditCurrentRaw.setText(str(value))
        if self.converter is not None:
            real = QApplication.instance().convertToUserAndFormat(self.converter.convert(value), self.baseUnit, 1)
            self.ui.lineEditCurrentConverted.setText(real)

    def newPoints(self, points):
        self.clearing = True
        self.ui.tableWidgetPoints.setRowCount(len(points))
        for row, point in enumerate(points):
            self.ui.tableWidgetPoints.setItem(row, 0, QTableWidgetItem(str(point.raw)))
            try:
                conv = str(round(self.app.convertToUserUnits(point.converted, self.baseUnit), 6))
            except TypeError:
                conv = '-'
            self.ui.tableWidgetPoints.setItem(row, 1, QTableWidgetItem(conv))
        self.clearing = False

    def newGraphPoints(self, points):
        self.ui.widgetGraph.plotPoints(points)

    def newRegression(self, points):
        if points is not None:
            self.ui.widgetGraph.plotLine(points)
            self.ui.widgetGraph.displayR(points[2])
        else:
            self.ui.widgetGraph.clearLine()
            self.ui.widgetGraph.displayR(0)

    def newConverter(self, converter):
        self.converter = converter
        self.ui.pushButtonSave.setEnabled(converter is not None)
        if converter is None:
            self.ui.lineEditCurrentConverted.setText('-')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space:
            self.capturePressed()

    def capturePressed(self):
        self.calibration.capture()

    def cellChanged(self, row, col):
        if not self.clearing and col == 1:
            value = self.ui.tableWidgetPoints.item(row, col).text()
            try:
                conv = QApplication.instance().convertFromUserUnits(float(value), self.baseUnit)
                self.calibration.setReal(row, conv)
            except ValueError:
                logger.log('Invalid value "{}" entered to cell ({}, {})'.format(value, row, col))
        self.ui.tableWidgetPoints.clearSelection()
        self.ui.pushButtonCapture.setFocus()

    def removePressed(self):
        selected = self.ui.tableWidgetPoints.selectionModel().selectedIndexes()
        if len(selected) > 0:
            self.calibration.delete(selected[0].row())

    def savePressed(self):
        self.save()
        self.exitCalibration()
        self.back.emit()

    def save(self):
        self.app.sensorProfileManager.addProfile(self.converter)

    # Returns true if it is safe to exit
    def unsavedCheck(self):
        if self.calibration is None or len(self.calibration.points) == 0:
            return True

        msg = QMessageBox()
        msg.setText("The calibration has not been saved. Close anyway?")
        msg.setWindowTitle("Close without saving?")
        msg.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        res = msg.exec()

        if res == QMessageBox.StandardButton.Discard:
            logger.log('User chose to discard results')
            return True
        if res == QMessageBox.StandardButton.Save:
            logger.log('User chose to save first')
            self.save()
            return True
        return False

    def backPressed(self):
        if not self.unsavedCheck():
            return
        self.exitCalibration()
        self.back.emit()

    def newInfo(self, properties):
        if properties['type'] == 'Load Cell':
            self.baseUnit = 'N'
            field = 'Force'
        else:
            self.baseUnit = 'Pa'
            field = 'Pressure'
        logger.log('Set base unit to "{}"'.format(self.baseUnit))
        self.ui.tableWidgetPoints.setHorizontalHeaderLabels(
            ['Raw', '{} ({})'.format(field, self.app.getUserUnit(self.baseUnit))]
        )
        self.ui.widgetGraph.setUnit(field, self.baseUnit)

    def exitCalibration(self):
        if self.calibration is not None:
            self.calibration.exit()
        self.calibration = None
