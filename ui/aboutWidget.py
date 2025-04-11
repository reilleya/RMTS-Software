from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget

from lib.boardInfoCollector import BoardInfoCollector
from lib.versions import getHardwareRevisionString, getFirmwareRevisionString
from lib.logger import logger

from ui.views.AboutWidget_ui import Ui_AboutWidget

class AboutWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_AboutWidget()
        self.ui.setupUi(self)
        self.ui.pushButtonBack.pressed.connect(self.backPressed)
        self.ui.pushButtonConnect.pressed.connect(self.connect)

        logo = QSvgWidget()
        self.ui.widgetLogo.setLayout(QVBoxLayout())
        self.ui.widgetLogo.layout().addWidget(logo)
        logo.load(QApplication.instance().getLogoPath())

        self.reset()

    def reset(self):
        self.ui.widgetPortSelector.refreshPorts()
        self.toggleConnectionButtons(False)
        self.boardInfoCollector = None
        self.ui.widgetDataAge.reset(False)

        versionString = '.'.join(str(num) for num in QApplication.instance().VERSION)
        self.ui.labelSoftwareVersion.setText('Rocket Motor Test System - {}'.format(versionString))

    def connect(self):
        self.boardInfoCollector = BoardInfoCollector(self.ui.widgetPortSelector.getPort())
        self.boardInfoCollector.error.connect(self.displayErrors)
        self.boardInfoCollector.version.connect(self.displayVersion)
        self.boardInfoCollector.disconnected.connect(self.disconnect)
        self.ui.pushButtonDisconnect.pressed.connect(self.boardInfoCollector.exit)
        self.ui.widgetDataAge.start()
        self.boardInfoCollector.resetDataAge.connect(self.ui.widgetDataAge.reset)
        self.boardInfoCollector.connect()
        self.toggleConnectionButtons(True)

    def displayVersion(self, versionInfo):
        self.ui.lineEditHardwareVersion.setText(getHardwareRevisionString(versionInfo['hardware']))
        self.ui.lineEditFirmwareVersion.setText(getFirmwareRevisionString(versionInfo['firmware']))

    def displayErrors(self, errors):
        self.ui.lineEditSD.setText(errors[0])
        self.ui.lineEditADC.setText(errors[1])
        self.ui.lineEditRadio.setText(errors[2])

    def toggleConnectionButtons(self, connected):
        self.ui.pushButtonConnect.setEnabled(not connected)
        self.ui.widgetPortSelector.setEnabled(not connected)
        self.ui.pushButtonDisconnect.setEnabled(connected)

    def clearOutput(self):
        self.ui.lineEditHardwareVersion.setText('-')
        self.ui.lineEditFirmwareVersion.setText('-')
        self.ui.lineEditSD.setText('-')
        self.ui.lineEditADC.setText('-')
        self.ui.lineEditRadio.setText('-')

    def disconnect(self):
        self.clearOutput()
        self.toggleConnectionButtons(False)
        self.ui.widgetDataAge.reset(False)

    def backPressed(self):
        self.exit()
        self.back.emit()

    def exit(self):
        if self.boardInfoCollector is not None:
            self.boardInfoCollector.exit()
