import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from lib.radio import RadioManager, SetupPacket, FirePacket, ResultPacket, StopPacket
from lib.firing import FiringConfig, Firing
from ui.views.FireWidget_ui import Ui_FireWidget

class LowPass():
    def __init__(self, historyLength):
        self.maxSize = historyLength
        self._buffer = []

    def addData(self, data):
        self._buffer.append(data)
        if len(self._buffer) > self.maxSize:
            self._buffer.pop(0)
        return sum(self._buffer) / len(self._buffer)

class FireWidget(QWidget):

    setup = pyqtSignal()
    fire = pyqtSignal()
    stop = pyqtSignal()
    results = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_FireWidget()
        self.ui.setupUi(self)

        self.setupFields = [
                            self.ui.widgetPortSelector, self.ui.widgetTransducerSelector, self.ui.firingConfig,
                            self.ui.pushButtonConnect
                           ]

        self.ui.pushButtonConnect.pressed.connect(self.connect)

        self.ui.lineEditArm.textChanged.connect(self.armBoxTextChanged)
        self.ui.lineEditStop.textChanged.connect(self.stopBoxTextChanged)
        self.ui.pushButtonFire.pressed.connect(self.fireButtonPressed)
        self.ui.pushButtonStop.pressed.connect(self.stop.emit)

        #self.ui.pushButtonSetup.pressed.connect(self.setupButtonPressed)
        #self.ui.pushButtonResults.pressed.connect(self.results.emit)

        self.reset()

    def reset(self):
        self.tared = False
        self.tareData = []
        self.tareOffset = 0
        self.radioManager = RadioManager()

        self.forceConv = None # Move to firing?
        self.pressConv = None

        self.forceBuff = LowPass(5)
        self.pressureBuff = LowPass(5)

        # Setup
        self.toggleSetupFields(True)
        self.ui.widgetTransducerSelector.reset()
        self.ui.firingConfig.loadProperties(FiringConfig())

        # Fire
        self.ui.pushButtonStop.setEnabled(False)
        self.ui.pushButtonFire.setEnabled(False)
        self.ui.pushButtonResults.setEnabled(True)

    def toggleSetupFields(self, enabled):
        for field in self.setupFields:
            field.setEnabled(enabled)

    def connect(self):
        port = self.ui.widgetPortSelector.getPort()
        self.forceConv, self.pressConv = self.ui.widgetTransducerSelector.getConverters()

        self.firing = Firing()

        self.radioManager.run(port)
        self.radioManager.newPacket.connect(self.newPacket)

        self.toggleSetupFields(False)

    def newPacket(self, packet):
        if type(packet) is SetupPacket:
            if self.tared:
                realForce = self.forceConv.convert(self.forceBuff.addData(packet.force)) - self.tareOffset
                self.ui.lineEditForce.setText(QApplication.instance().convertToUserAndFormat(realForce, 'N', 1))
            else:
                self.tareData.append(packet.force)
                if len(self.tareData) == 10:
                    self.tareOffset = self.forceConv.convert(sum(self.tareData) / len(self.tareData))
                    self.tared = True
            realPressure = self.pressConv.convert(self.pressureBuff.addData(packet.pressure))
            self.ui.lineEditPressure.setText(QApplication.instance().convertToUserAndFormat(realPressure, 'Pa', 1))
            self.ui.lineEditContinuity.setText("Yes" if packet.continuity else "No")
        #if type(packet) is ResultPacket:
        #    if self.firing is not None:
        #        self.firing.addDatapoint(packet)
        #    else:
        #        print('Got results packet without a firing to add it to')

    def setupButtonPressed(self):
        self.reset()
        self.setup.emit()

    def armBoxTextChanged(self):
        self.ui.pushButtonFire.setEnabled(self.ui.lineEditArm.text() == "ARM")

    def stopBoxTextChanged(self):
        self.ui.pushButtonStop.setEnabled(self.ui.lineEditStop.text() == "STOP")

    def fireButtonPressed(self):
        self.ui.pushButtonResults.setEnabled(True)
        self.fire.emit()
