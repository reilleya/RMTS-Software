import sys

from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal

from lib.filter import LowPass
from lib.radio import RadioManager, SetupPacket, FirePacket, ResultPacket, StopPacket
from lib.motor import FiringConfig
from lib.firing import Firing
from lib.logger import logger
from .errorCollector import ErrorCollector
from ui.views.FireWidget_ui import Ui_FireWidget

class FireWidget(QWidget):

    back = pyqtSignal()
    results = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_FireWidget()
        self.ui.setupUi(self)

        self.setupFields = [
                            self.ui.widgetPortSelector, self.ui.widgetTransducerSelector, self.ui.firingConfig,
                            self.ui.pushButtonConnect
                           ]
        self.firingFields = [
                                self.ui.lineEditArm, self.ui.lineEditStop
                            ]
        self.resultsFields = [
                                self.ui.lineEditInitialResults
                             ]

        self.ui.pushButtonConnect.pressed.connect(self.connect)

        self.ui.lineEditArm.textChanged.connect(self.armBoxTextChanged)
        self.ui.lineEditStop.textChanged.connect(self.stopBoxTextChanged)
        self.ui.pushButtonFire.pressed.connect(self.fireButtonPressed)
        self.ui.pushButtonFire.released.connect(self.fireButtonReleased)
        self.ui.pushButtonStop.pressed.connect(self.stopButtonPressed)

        self.ui.firingConfig.setPreferences(QApplication.instance().getPreferences())

        self.ui.pushButtonBack.pressed.connect(self.backPressed)

        self.reset()

    def reset(self):
        self.tared = False
        self.tareDataForce = []
        self.tareOffsetForce = 0
        self.tareDataPressure = []
        self.tareOffsetPressure = 0

        self.firing = None

        self.errorCollector = ErrorCollector()
        self.errorCollector.hasError.connect(self.hasError)

        self.forceConv = None # Move to firing?
        self.pressConv = None

        self.forceBuff = LowPass(5)
        self.pressureBuff = LowPass(5)

        # Setup
        self.ui.widgetPortSelector.refreshPorts()
        self.toggleFields(self.setupFields, True)
        self.ui.widgetTransducerSelector.reset()
        self.ui.firingConfig.loadProperties(FiringConfig({'cutoffThreshold': 5}))

        # Fire
        self.toggleFields(self.firingFields, False)
        self.emptyFiringControls()

        self.ui.lineEditForce.setText('-')
        self.ui.lineEditPressure.setText('-')
        self.ui.lineEditContinuity.setText('-')

        self.ui.pushButtonStop.setEnabled(False)
        self.ui.pushButtonFire.setEnabled(False)
        self.ui.widgetDataAge.reset(False)

        # Results
        self.toggleFields(self.resultsFields, False)
        self.ui.lineEditInitialResults.setText('0 s')

    def emptyFiringControls(self):
        self.ui.lineEditArm.setText('')
        self.ui.lineEditStop.setText('')

    def toggleFields(self, fields, enabled):
        for field in fields:
            field.setEnabled(enabled)

    def connect(self):
        logger.log('Connect clicked, setting up firing')
        port = self.ui.widgetPortSelector.getPort()
        self.forceConv, self.pressConv = self.ui.widgetTransducerSelector.getConverters()
        if self.forceConv == None and self.pressConv == None:
            QApplication.instance().outputMessage('At least one transducer must be used.')
            logger.log('Both transducers set to "None", cancelling')
            return
        forceConvName = 'None'
        if self.forceConv is not None:
            forceConvName = self.forceConv.getProperty('name')
        pressureConvName = 'None'
        if self.pressConv is not None:
            pressureConvName = self.pressConv.getProperty('name')
        logger.log('Using LC profile: "{}", PT: "{}"'.format(forceConvName, pressureConvName))

        fireData = FiringConfig()
        fireData.setProperties(self.ui.firingConfig.getProperties())
        logger.log('Firing properties: {}'.format(fireData.getProperties()))
        self.firing = Firing(self.forceConv, self.pressConv, fireData, port)
        self.firing.newSetupPacket.connect(self.newSetupPacket)
        self.firing.newErrorPacket.connect(self.errorCollector.recordError)
        self.firing.newFiringPacket.connect(self.newFiringPacket)
        self.firing.fullSizeKnown.connect(self.gotoResults)
        self.firing.newResultsPacket.connect(QApplication.instance().newResultsPacket)
        self.firing.newGraph.connect(QApplication.instance().newResult)
        self.firing.stopped.connect(lambda: self.toggleFields(self.resultsFields, True))
        self.firing.initialResultsTime.connect(self.initialResultsTime)

        self.ui.widgetDataAge.start()
        self.firing.newSetupPacket.connect(self.ui.widgetDataAge.reset)
        self.firing.newErrorPacket.connect(self.ui.widgetDataAge.reset)
        self.firing.newFiringPacket.connect(self.ui.widgetDataAge.reset)
        self.toggleFields(self.setupFields, False)
        self.toggleFields(self.firingFields, True)

    def newSetupPacket(self, packet):
        if self.tared:
            if self.forceConv is not None:
                realForce = self.forceConv.convert(self.forceBuff.addData(packet.force)) - self.tareOffsetForce
                self.ui.lineEditForce.setText(QApplication.instance().convertToUserAndFormat(realForce, 'N', 1))
            if self.pressConv is not None:
                realPressure = self.pressConv.convert(self.pressureBuff.addData(packet.pressure)) - self.tareOffsetPressure
                self.ui.lineEditPressure.setText(QApplication.instance().convertToUserAndFormat(realPressure, 'Pa', 1))
        else:
            self.tareDataForce.append(packet.force)
            self.tareDataPressure.append(packet.pressure)
            if len(self.tareDataForce) == 10:
                logger.log('Tare complete')
                self.tared = True
                if self.forceConv is not None:
                    tareAvgForce = sum(self.tareDataForce) / len(self.tareDataForce)
                    self.tareOffsetForce = self.forceConv.convert(tareAvgForce)
                    logger.log('\tForce offset = ({:.4f} conv, {:.4f} raw)'.format(self.tareOffsetForce, tareAvgForce))
                if self.pressConv is not None:
                    tareAvgPressure = sum(self.tareDataPressure) / len(self.tareDataPressure)
                    self.tareOffsetPressure = self.pressConv.convert(tareAvgPressure)
                    logger.log('\tPressure offset = ({:.4f} conv, {:.4f} raw)'.format(self.tareOffsetPressure,
                        tareAvgPressure))

        self.ui.lineEditContinuity.setText("Yes" if packet.continuity else "No")

    def newFiringPacket(self, packet):
        self.ui.lineEditForce.setText('FIRING')
        self.ui.lineEditPressure.setText('FIRING')
        self.ui.lineEditContinuity.setText("Yes" if packet.continuity else "No")

    def initialResultsTime(self, time):
        self.ui.lineEditForce.setText('Stopped')
        self.ui.lineEditPressure.setText('Stopped')
        self.ui.lineEditContinuity.setText("-")
        self.ui.lineEditInitialResults.setText('{:.2f} s'.format(time))

    def armBoxTextChanged(self):
        enabled = self.ui.lineEditArm.text() == "ARM"
        self.ui.pushButtonFire.setEnabled(enabled)
        if enabled:
            logger.log('Fire button enabled')

    def stopBoxTextChanged(self):
        self.ui.pushButtonStop.setEnabled(self.ui.lineEditStop.text() == "STOP")

    def fireButtonPressed(self):
        if self.firing is None:
            logger.error("Tried to fire without a firing!")
            return
        logger.log('Fire button pressed')
        self.firing.fire()

    def fireButtonReleased(self):
        if self.firing is None:
            return
        logger.log('Fire button released')
        self.firing.stopFiring()

    def stopButtonPressed(self):
        if self.firing is None:
            logger.error("Tried to stop without a firing!")
            return
        logger.log('Stop button pressed')
        self.toggleFields(self.firingFields, False)
        self.emptyFiringControls()
        self.firing.stop()

    def gotoResults(self, resultsSize):
        self.results.emit()
        QApplication.instance().configureLiveResults(resultsSize)

    def exit(self):
        if self.firing is not None:
            self.firing.exit()

    def backPressed(self):
        if not self.exitCheck():
            return
        self.exit()
        self.back.emit()

    def hasError(self):
        self.toggleFields(self.firingFields, False)

    def exitCheck(self):
        if self.firing is None:
            return True
        logger.log('Checking if user really wants to exit firing widget')
        msg = QMessageBox()
        msg.setText("The radio is currently connected. Close anyway?")
        msg.setWindowTitle("Close while connected?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        res = msg.exec_()
        if res == QMessageBox.Yes:
            logger.log('User chose to close')
            return True
        if res == QMessageBox.No:
            logger.log('User chose to stay on page')
            return False
        return False
