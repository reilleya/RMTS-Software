from PyQt5.QtWidgets import QWidget, QApplication

from ui.views.TransducerSelectorWidget_ui import Ui_TransducerSelectorWidget

class TransducerSelectorWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.ui = Ui_TransducerSelectorWidget()
        self.ui.setupUi(self)

        self.transducerManger = QApplication.instance().sensorProfileManager

        self.ui.comboBoxLoadCell.currentTextChanged.connect(self.updateMaxForceLabel)
        self.ui.comboBoxPressureTransducer.currentTextChanged.connect(self.updateMaxPressureLabel)

    def reset(self):
        self.ui.comboBoxLoadCell.clear()
        self.ui.comboBoxLoadCell.addItems(self.transducerManger.getProfileNames('Load Cell'))
        self.ui.comboBoxLoadCell.addItem('None')
        self.ui.comboBoxPressureTransducer.clear()
        self.ui.comboBoxPressureTransducer.addItems(self.transducerManger.getProfileNames('Pressure Transducer'))
        self.ui.comboBoxPressureTransducer.addItem('None')
        self.updateMaxForceLabel()
        self.updateMaxPressureLabel()

    def getConverters(self):
        force = self.transducerManger.getProfile(self.ui.comboBoxLoadCell.currentText())
        press = self.transducerManger.getProfile(self.ui.comboBoxPressureTransducer.currentText())
        return [force, press]

    def updateMaxForceLabel(self):
        lcName = self.ui.comboBoxLoadCell.currentText()
        if lcName in self.transducerManger.getProfileNames('Load Cell'):
            loadCell = self.transducerManger.getProfile(lcName)
            labelText = 'Max: {}'.format(QApplication.instance().convertToUserAndFormat(loadCell.getMax(), 'N', 1))
            self.ui.labelMaxForce.setText(labelText)
        else:
            self.ui.labelMaxForce.setText('Max: -')

    def updateMaxPressureLabel(self):
        ptName = self.ui.comboBoxPressureTransducer.currentText()
        if ptName in self.transducerManger.getProfileNames('Pressure Transducer'):
            pressTrans = self.transducerManger.getProfile(ptName)
            labelText = 'Max: {}'.format(QApplication.instance().convertToUserAndFormat(pressTrans.getMax(), 'Pa', 1))
            self.ui.labelMaxPressure.setText(labelText)
        else:
            self.ui.labelMaxPressure.setText('Max: -')