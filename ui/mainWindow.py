import sys
from enum import IntEnum
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal

from ui.views.MainWindow_ui import Ui_MainWindow
from lib.logger import logger

class MainWindowPages(IntEnum):
    START = 0
    RAW_DATA_MOTOR_INFO = 1
    SETUP_FIRE = 2
    RESULTS = 3
    PREFERENCES = 4
    CALIBRATE = 5
    EDIT_TRANSDUCER = 6
    RECV_RESULTS = 7

PAGE_NAMES = {
    0: 'Start',
    1: 'Raw data motor info',
    2: 'Setup fire',
    3: 'Results',
    4: 'Preferences',
    5: 'Calibrate',
    6: 'Transducer editor',
    7: 'Receive results'
}

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.ui.pageStart.beginSetup.connect(self.gotoSetupPage)
        self.ui.pageStart.recvResults.connect(self.gotoRecvResultsPage)
        self.ui.pageStart.editPreferences.connect(self.gotoPreferencesPage)
        self.ui.pageStart.calibrate.connect(self.gotoCalibratePage)
        self.ui.pageStart.editTransducer.connect(self.gotoEditTransducerPage)
        self.ui.pageStart.showResultsPage.connect(lambda: self.gotoResultsPage(False))
        self.ui.pageStart.showRawData.connect(self.gotoRawDataMotorInfoPage)

        self.ui.pageRawDataMotorInfo.back.connect(self.gotoStartPage)
        self.ui.pageRawDataMotorInfo.nextPage.connect(lambda: self.gotoResultsPage(False))

        self.ui.pageFire.back.connect(self.gotoStartPage)
        self.ui.pageFire.results.connect(lambda: self.gotoResultsPage(True))

        self.ui.pageResults.back.connect(self.exitResults)

        self.ui.pagePreferences.back.connect(self.gotoStartPage)

        self.ui.pageCalibrate.back.connect(self.gotoStartPage)

        self.ui.pageEditTransducer.back.connect(self.gotoStartPage)

        self.ui.pageRecvResults.back.connect(self.gotoStartPage)
        self.ui.pageRecvResults.results.connect(lambda: self.gotoResultsPage(True))

    def closeEvent(self, event=None):
        self.closed.emit()
        self.ui.pageFire.exit()
        self.ui.pageCalibrate.exit()
        self.ui.pageRecvResults.exit()
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

    def gotoCalibratePage(self):
        self.gotoPage(MainWindowPages.CALIBRATE)

    def gotoPreferencesPage(self):
        self.ui.pagePreferences.setup()
        self.gotoPage(MainWindowPages.PREFERENCES)

    def gotoEditTransducerPage(self):
        self.ui.pageEditTransducer.setup()
        self.gotoPage(MainWindowPages.EDIT_TRANSDUCER)

    def gotoRecvResultsPage(self):
        self.ui.pageRecvResults.setup()
        self.gotoPage(MainWindowPages.RECV_RESULTS)

    def exitResults(self):
        self.ui.pageRecvResults.exit()
        self.ui.pageFire.exit()
        self.gotoStartPage()
