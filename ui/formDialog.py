from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon

from pyFormGen.collectionEditor import CollectionEditor
from pyFormGen.properties import PropertyCollection
from lib.logger import logger

class FormDialog(QDialog):

    submitted = pyqtSignal(dict)

    def __init__(self, title, description, propDict, values = None):
        super().__init__()
        self.title = title
        self.description = description
        self.preferences = None
        self.propCollection = PropertyCollection()
        self.propCollection.props = propDict

        if values is not None:
            self.propCollection.setProperties(values)

        self.setWindowTitle(self.title)
        self.setWindowIcon(QApplication.instance().icon)
        self.setLayout(QVBoxLayout())

        self.descLabel = QLabel(self.description)
        self.descLabel.setWordWrap(True)
        self.layout().addWidget(self.descLabel)

        self.editor = CollectionEditor(self, True)
        self.editor.setPreferences(QApplication.instance().getPreferences())
        self.editor.changeApplied.connect(self.applyPressed)
        self.editor.closed.connect(self.hide)
        self.layout().addWidget(self.editor)


    def show(self):
        logger.log('Showing "{}" dialog'.format(self.title))
        self.editor.loadProperties(self.propCollection)
        super().show()

    def applyPressed(self, properties):
        logger.log('Applying "{}" from "{}" dialog'.format(properties, self.title))
        self.submitted.emit(properties)
