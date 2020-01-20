from PyQt5.QtWidgets import QWidget, QApplication

from lib.converter import ConverterType
from ui.views.TransducerSelectorWidget_ui import Ui_TransducerSelectorWidget

class TransducerSelectorWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.ui = Ui_TransducerSelectorWidget()
        self.ui.setupUi(self)

        self.transducerManger = QApplication.instance().sensorProfileManager

    def reset(self):
        self.ui.comboBoxLoadCell.clear()
        self.ui.comboBoxLoadCell.addItems(self.transducerManger.getProfileNames(ConverterType.LOAD_CELL))
        self.ui.comboBoxPressureTransducer.addItems(self.transducerManger.getProfileNames(ConverterType.PRESSURE_TRANSDUCER))

    def getConverters(self):
        force = self.transducerManger.getProfile(self.ui.comboBoxLoadCell.currentText())
        press = self.transducerManger.getProfile(self.ui.comboBoxPressureTransducer.currentText())
        return [force, press]
