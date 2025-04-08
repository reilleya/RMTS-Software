import sys
from enum import IntEnum
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon

from ui.views.MainWindow_ui import Ui_MainWindow
from lib.logger import logger

class MainWindowPages(IntEnum):
    START = 0
    RAW_DATA_MOTOR_INFO = 1
    SETUP_FIRE = 2
    RESULTS = 3
    PREFERENCES = 4
    CALIBRATION = 5
    EDIT_TRANSDUCER = 6
    RECV_RESULTS = 7
    CALIBRATION_SETUP = 8
    ABOUT = 9

PAGE_NAMES = {
    0: 'Start',
    1: 'Raw data motor info',
    2: 'Setup fire',
    3: 'Results',
    4: 'Preferences',
    5: 'Calibration',
    6: 'Transducer editor',
    7: 'Receive results',
    8: 'Calibration setup',
    9: 'About'
}

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.setWindowIcon(QIcon('resources/icon.png'))

        self.ui.pageStart.beginSetup.connect(self.gotoSetupPage)
        self.ui.pageStart.recvResults.connect(self.gotoRecvResultsPage)
        self.ui.pageStart.editPreferences.connect(self.gotoPreferencesPage)
        self.ui.pageStart.calibrate.connect(self.gotoCalibrationSetupPage)
        self.ui.pageStart.editTransducer.connect(self.gotoEditTransducerPage)
        self.ui.pageStart.showResultsPage.connect(lambda: self.gotoResultsPage(False))
        self.ui.pageStart.showRawData.connect(self.gotoRawDataMotorInfoPage)
        self.ui.pageStart.showAbout.connect(self.gotoAboutPage)

        self.ui.pageRawDataMotorInfo.back.connect(self.gotoStartPage)
        self.ui.pageRawDataMotorInfo.nextPage.connect(lambda: self.gotoResultsPage(False))

        self.ui.pageFire.back.connect(self.gotoStartPage)
        self.ui.pageFire.results.connect(lambda: self.gotoResultsPage(True))

        self.ui.pageResults.back.connect(self.exitResults)

        self.ui.pagePreferences.back.connect(self.gotoStartPage)

        self.ui.pageCalibration.back.connect(self.gotoStartPage)

        self.ui.pageEditTransducer.back.connect(self.gotoStartPage)

        self.ui.pageRecvResults.back.connect(self.gotoStartPage)
        self.ui.pageRecvResults.results.connect(lambda: self.gotoResultsPage(True))

        self.ui.pageCalibrationSetup.back.connect(self.gotoStartPage)
        self.ui.pageCalibrationSetup.nextPage.connect(self.gotoCalibrationPage)

        self.ui.pageAbout.back.connect(self.gotoStartPage)

    def closeEvent(self, event=None):
        if (
            not self.ui.pageFire.exitCheck()
            or not self.ui.pageResults.unsavedCheck()
            or not self.ui.pageCalibration.unsavedCheck()
        ):
            logger.log('Canceling close event')
            if event is not None and not isinstance(event, bool):
                    event.ignore()
            return
        self.closed.emit()
        self.ui.pageFire.exit()
        self.ui.pageRecvResults.exit()
        self.ui.pageCalibrationSetup.exit()
        self.ui.pageAbout.exit()
        logger.log('Application exited')
        sys.exit()

    def gotoPage(self, page):
        logger.log('Navigating to "{}" page (id = {})'.format(PAGE_NAMES[page], page))
        self.ui.stackedWidget.setCurrentIndex(int(page))

    def gotoStartPage(self):
        self.gotoPage(MainWindowPages.START)

    def gotoSetupPage(self):
        self.ui.pageFire.reset()
        self.gotoPage(MainWindowPages.SETUP_FIRE)

    def gotoRawDataMotorInfoPage(self, raw):
        self.ui.pageRawDataMotorInfo.setup(raw)
        self.gotoPage(MainWindowPages.RAW_DATA_MOTOR_INFO)

    def gotoResultsPage(self, reset):
        if reset:
            self.ui.pageResults.reset()
        self.gotoPage(MainWindowPages.RESULTS)

    def gotoCalibrationSetupPage(self):
        self.ui.pageCalibrationSetup.reset()
        self.ui.pageCalibration.reset()
        self.gotoPage(MainWindowPages.CALIBRATION_SETUP)

    def gotoCalibrationPage(self):
        self.gotoPage(MainWindowPages.CALIBRATION)

    def gotoPreferencesPage(self):
        self.ui.pagePreferences.setup()
        self.gotoPage(MainWindowPages.PREFERENCES)

    def gotoEditTransducerPage(self):
        self.ui.pageEditTransducer.setup()
        self.gotoPage(MainWindowPages.EDIT_TRANSDUCER)

    def gotoRecvResultsPage(self):
        self.ui.pageRecvResults.reset()
        self.gotoPage(MainWindowPages.RECV_RESULTS)

    def exitResults(self):
        self.ui.pageRecvResults.exit()
        self.ui.pageFire.exit()
        self.gotoStartPage()

    def gotoAboutPage(self):
        self.ui.pageAbout.reset()
        self.gotoPage(MainWindowPages.ABOUT)
