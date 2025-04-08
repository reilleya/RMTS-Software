import sys
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import pyqtSignal

from ui.views.PreferencesWidget_ui import Ui_PreferencesWidget
from pyFormGen.unitPreferences import UnitPreferences

class PreferencesWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_PreferencesWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonNext.pressed.connect(self.nextPressed)
        self.ui.pushButtonBack.pressed.connect(self.back.emit)
        
    def setup(self):
        self.ui.preferences.loadProperties(QApplication.instance().preferencesManager.preferences)

    def nextPressed(self):
        QApplication.instance().preferencesManager.setPreferences(UnitPreferences(self.ui.preferences.getProperties()))
        self.back.emit()
