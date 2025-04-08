from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import pyqtSignal

from lib.radio import RadioManager, SetupPacket
from lib.converter import BaseConverter
from lib.calibration import Calibration
from .errorCollector import ErrorCollector

from ui.views.CalibrationSetupWidget_ui import Ui_CalibrationSetupWidget

class CalibrationSetupWidget(QWidget):

    back = pyqtSignal()
    nextPage = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_CalibrationSetupWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonConnect.pressed.connect(self.connect)

        self.ui.pushButtonBack.pressed.connect(self.backPressed)
        self.ui.pushButtonNext.pressed.connect(self.nextPressed)

        self.reset()

    def reset(self):
        self.ui.widgetPortSelector.refreshPorts()
        self.errorCollector = ErrorCollector()
        self.errorCollector.newError.connect(lambda: self.ui.pushButtonNext.setEnabled(False))
        self.ui.widgetBasicInfo.loadProperties(BaseConverter())
        self.ui.pushButtonNext.setEnabled(False)
        self.ui.widgetDataAge.reset(False)
        self.toggleConnectFields(True)
        self.calibration = None

    def toggleConnectFields(self, enabled):
        self.ui.pushButtonConnect.setEnabled(enabled)
        self.ui.widgetPortSelector.setEnabled(enabled)

    def connect(self):
        port = self.ui.widgetPortSelector.getPort()
        baseConfig = self.ui.widgetBasicInfo.getProperties()
        self.calibration = Calibration(port, baseConfig)
        self.calibration.resetDataAge.connect(self.ui.widgetDataAge.reset)
        self.calibration.errorPacket.connect(self.errorCollector.recordError)
        self.calibration.ready.connect(lambda: self.ui.pushButtonNext.setEnabled(True))
        self.calibration.done.connect(self.reset)
        QApplication.instance().newCalibration(self.calibration)
        self.ui.widgetDataAge.start()
        self.calibration.connect()
        self.toggleConnectFields(False)

    def backPressed(self):
        self.exit()
        self.reset()
        self.back.emit()

    def nextPressed(self):
        self.calibration.updateInfo(self.ui.widgetBasicInfo.getProperties())
        self.nextPage.emit()

    def exit(self):
        if self.calibration is not None:
            self.calibration.exit()
        self.calibration = None
