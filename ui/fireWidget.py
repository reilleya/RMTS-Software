import sys

from PyQt5.QtWidgets import QWidget, QApplication
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
        self.ui.pushButtonStop.pressed.connect(self.stopButtonPressed)

        self.ui.firingConfig.setPreferences(QApplication.instance().getPreferences())

        self.ui.pushButtonBack.pressed.connect(self.backPressed)

        self.reset()

    def reset(self):
        self.tared = False
        self.tareData = []
        self.tareOffset = 0

        self.firing = None

        self.errorCollector = ErrorCollector()
        self.errorCollector.hasError.connect(self.hasError)

        self.forceConv = None # Move to firing?
        self.pressConv = None

        self.forceBuff = LowPass(5)
        self.pressureBuff = LowPass(5)

        # Setup
        self.toggleFields(self.setupFields, True)
        self.ui.widgetTransducerSelector.reset()
        self.ui.firingConfig.loadProperties(FiringConfig())

        # Fire
        self.toggleFields(self.firingFields, False)
        self.ui.lineEditArm.setText('')
        self.ui.lineEditStop.setText('')
        self.ui.pushButtonStop.setEnabled(False)
        self.ui.pushButtonFire.setEnabled(False)
        self.ui.widgetDataAge.reset(False)

        # Results
        self.toggleFields(self.resultsFields, False)
        self.ui.lineEditInitialResults.setText('0 s')


    def toggleFields(self, fields, enabled):
        for field in fields:
            field.setEnabled(enabled)

    def connect(self):
        logger.log('Connect clicked, setting up firing')
        port = self.ui.widgetPortSelector.getPort()
        self.forceConv, self.pressConv = self.ui.widgetTransducerSelector.getConverters()
        trans = 'Using LC profile: "{}", PT: "{}"'
        logger.log(trans.format(self.forceConv.getProperty('name'), self.pressConv.getProperty('name')))

        fireData = FiringConfig()
        fireData.setProperties(self.ui.firingConfig.getProperties())
        logger.log('Firing properties: {}'.format(fireData.getProperties()))
        self.firing = Firing(self.forceConv, self.pressConv, fireData, port)
        self.firing.newSetupPacket.connect(self.newPacket)
        self.firing.newErrorPacket.connect(self.errorCollector.recordError)
        self.firing.fullSizeKnown.connect(self.gotoResults)
        self.firing.newResultsPacket.connect(QApplication.instance().newResultsPacket)
        self.firing.newGraph.connect(QApplication.instance().newResult)
        self.firing.stopped.connect(lambda: self.toggleFields(self.resultsFields, True))
        self.firing.initialResultsTime.connect(self.initialResultsTime)

        self.ui.widgetDataAge.start()
        self.firing.newSetupPacket.connect(self.ui.widgetDataAge.reset)
        self.firing.newErrorPacket.connect(self.ui.widgetDataAge.reset)
        self.toggleFields(self.setupFields, False)
        self.toggleFields(self.firingFields, True)

    def newPacket(self, packet):
        if self.tared:
            realForce = self.forceConv.convert(self.forceBuff.addData(packet.force)) - self.tareOffset
            self.ui.lineEditForce.setText(QApplication.instance().convertToUserAndFormat(realForce, 'N', 1))
        else:
            self.tareData.append(packet.force)
            if len(self.tareData) == 10:
                tareAvg = sum(self.tareData) / len(self.tareData)
                self.tareOffset = self.forceConv.convert(tareAvg)
                self.tared = True
                logger.log('Tare complete, offset = ({:.4f} conv, {:.4f} raw)'.format(self.tareOffset, tareAvg))
        realPressure = self.pressConv.convert(self.pressureBuff.addData(packet.pressure))
        self.ui.lineEditPressure.setText(QApplication.instance().convertToUserAndFormat(realPressure, 'Pa', 1))
        self.ui.lineEditContinuity.setText("Yes" if packet.continuity else "No")

    def initialResultsTime(self, time):
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

    def stopButtonPressed(self):
        if self.firing is None:
            logger.error("Tried to stop without a firing!")
            return
        logger.log('Stop button pressed')
        self.firing.stop()

    def gotoResults(self, resultsSize):
        self.results.emit()
        QApplication.instance().configureLiveResults(resultsSize)

    def exit(self): # TODO: confirm before closing if connected to radio
        if self.firing is not None:
            self.firing.exit()

    def backPressed(self): # TODO: confirm before closing if connected to radio
        if self.firing is not None:
            self.firing.exit()
        self.back.emit()

    def hasError(self):
        self.toggleFields(self.firingFields, False)
