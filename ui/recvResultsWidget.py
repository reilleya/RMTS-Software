import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from lib.filter import LowPass
from lib.radio import RadioManager, SetupPacket, FirePacket, ResultPacket, StopPacket
from lib.motor import MotorConfig
from lib.firing import Firing
from ui.views.RecvResultsWidget_ui import Ui_RecvResultsWidget

class RecvResultsWidget(QWidget):

    back = pyqtSignal()
    results = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_RecvResultsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonConnect.pressed.connect(self.connect)

        self.ui.widgetMotorConfig.setPreferences(QApplication.instance().getPreferences())

        self.ui.pushButtonBack.pressed.connect(self.back.emit)

        self.reset()

    def reset(self):
        self.ui.widgetPortSelector.refreshPorts()
        self.ui.widgetMotorConfig.loadProperties(MotorConfig({'cutoffThreshold': 5}))
        self.ui.widgetTransducerSelector.reset()
        self.ui.lineEditInitialResults.setText('0 s')
        self.ui.pushButtonConnect.setEnabled(True)
        self.firing = None

    def connect(self):
        self.ui.pushButtonConnect.setEnabled(False)
        port = self.ui.widgetPortSelector.getPort()
        self.forceConv, self.pressConv = self.ui.widgetTransducerSelector.getConverters()

        motorConfig = MotorConfig()
        motorConfig.setProperties(self.ui.widgetMotorConfig.getProperties())
        self.firing = Firing(self.forceConv, self.pressConv, motorConfig, port)
        self.firing.newGraph.connect(QApplication.instance().newResult)
        self.firing.fullSizeKnown.connect(self.gotoResults)
        self.firing.newResultsPacket.connect(QApplication.instance().newResultsPacket)
        self.firing.initialResultsTime.connect(self.initialResultsTime)

    def initialResultsTime(self, time):
        self.ui.lineEditInitialResults.setText('{:.2f} s'.format(time))

    def gotoResults(self, resultsSize):
        self.results.emit()
        QApplication.instance().configureLiveResults(resultsSize)

    def exit(self): # TODO: confirm before closing if connected to radio
        if self.firing is not None:
            self.firing.exit()
