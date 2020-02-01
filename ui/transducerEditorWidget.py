from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from lib.converter import Converter

from ui.views.TransducerEditorWidget_ui import Ui_TransducerEditorWidget

class TransducerEditorWidget(QWidget):

    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.manager = QApplication.instance().sensorProfileManager
        self.ui = Ui_TransducerEditorWidget()
        self.ui.setupUi(self)

        self.selectedButtons = [
            self.ui.pushButtonRemove, self.ui.pushButtonEdit
        ]

        self.ui.pushButtonBack.pressed.connect(self.back.emit)

        self.ui.widgetProfileEditor.addButtons()
        self.ui.widgetProfileEditor.changeApplied.connect(self.profileEdited)
        self.ui.widgetProfileEditor.closed.connect(self.editorClosed)

        self.ui.listWidgetProfiles.currentItemChanged.connect(lambda: self.toggleSelectedButtons(True))

        self.ui.pushButtonAdd.pressed.connect(self.addNewProfile)
        self.ui.pushButtonRemove.pressed.connect(self.removeProfile)
        self.ui.pushButtonEdit.pressed.connect(self.editProfile)

    def setupProfileList(self):
        self.ui.listWidgetProfiles.clear()
        self.ui.listWidgetProfiles.addItems(self.manager.getProfileNames())

    def setup(self):
        self.setupProfileList()
        self.toggleSelectedButtons(False)

    def toggleSelectedButtons(self, state):
        for button in self.selectedButtons:
            button.setEnabled(state)

    def editorClosed(self):
        self.ui.pushButtonBack.setEnabled(True)
        self.ui.listWidgetProfiles.setEnabled(True)
        self.ui.pushButtonAdd.setEnabled(True)
        self.toggleSelectedButtons(True)

    def editProfile(self):
        self.ui.widgetProfileEditor.loadProperties(self.manager.profiles[self.ui.listWidgetProfiles.currentRow()])
        self.ui.pushButtonBack.setEnabled(False)
        self.ui.listWidgetProfiles.setEnabled(False)
        self.ui.pushButtonAdd.setEnabled(False)
        self.toggleSelectedButtons(False)

    def profileEdited(self, properties):
        self.manager.profiles[self.ui.listWidgetProfiles.currentRow()].setProperties(properties)
        self.manager.saveProfiles()
        self.setupProfileList()

    def addNewProfile(self):
        number = 1
        names = self.manager.getProfileNames()
        while "Transducer #{}".format(number) in names:
            number += 1
        props = {
            "name": "Transducer #{}".format(number),
            "offset": 0,
            "ratio": 0,
        }
        self.manager.profiles.append(Converter(props))
        self.manager.saveProfiles()
        self.setupProfileList()

    def removeProfile(self):
        del self.manager.profiles[self.ui.listWidgetProfiles.currentRow()]
        self.manager.saveProfiles()
        self.setupProfileList()
