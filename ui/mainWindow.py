import sys
from enum import IntEnum
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal

from ui.views.MainWindow_ui import Ui_MainWindow

class MainWindowPages(IntEnum):
    START = 0
    RAW_DATA_MOTOR_INFO = 1
    SETUP_FIRE = 2
    RESULTS = 3
    PREFERENCES = 4
    CALIBRATE = 5
    EDIT_TRANSDUCER = 6

class MainWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.app = app

        self.ui.pageStart.beginSetup.connect(self.gotoSetupPage)
        self.ui.pageStart.editPreferences.connect(self.gotoPreferencesPage)
        self.ui.pageStart.calibrate.connect(self.gotoCalibratePage)
        self.ui.pageStart.editTransducer.connect(self.gotoEditTransducerPage)
        self.ui.pageStart.showResultsPage.connect(self.gotoResultsPage)
        self.ui.pageStart.showRawData.connect(self.gotoRawDataMotorInfoPage)

        self.ui.pageRawDataMotorInfo.back.connect(self.gotoStartPage)
        self.ui.pageRawDataMotorInfo.nextPage.connect(self.gotoResultsPage)

        self.ui.pageFire.back.connect(self.gotoStartPage)
        self.ui.pageFire.results.connect(self.gotoResultsPage)

        self.ui.pageResults.back.connect(self.gotoStartPage)

        self.ui.pagePreferences.back.connect(self.gotoStartPage)

        self.ui.pageCalibrate.back.connect(self.gotoStartPage)

        self.ui.pageEditTransducer.back.connect(self.gotoStartPage)

    def closeEvent(self, event=None):
        self.closed.emit()
        self.ui.pageFire.exit()
        self.ui.pageCalibrate.exit()
        sys.exit()

    def gotoPage(self, page):
        self.ui.stackedWidget.setCurrentIndex(int(page))

    def gotoStartPage(self):
        self.gotoPage(MainWindowPages.START)

    def gotoSetupPage(self):
        self.ui.pageFire.reset()
        self.gotoPage(MainWindowPages.SETUP_FIRE)

    def gotoRawDataMotorInfoPage(self, raw):
        self.ui.pageRawDataMotorInfo.setup(raw)
        self.gotoPage(MainWindowPages.RAW_DATA_MOTOR_INFO)

    def gotoResultsPage(self):
        self.gotoPage(MainWindowPages.RESULTS)

    def gotoCalibratePage(self):
        self.gotoPage(MainWindowPages.CALIBRATE)

    def gotoPreferencesPage(self):
        self.ui.pagePreferences.setup()
        self.gotoPage(MainWindowPages.PREFERENCES)

    def gotoEditTransducerPage(self):
        self.ui.pageEditTransducer.setup()
        self.gotoPage(MainWindowPages.EDIT_TRANSDUCER)
