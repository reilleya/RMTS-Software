from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication

from ui.views.engExporterWidget_ui import Ui_engExporterWidget

from pyFormGen.properties import PropertyCollection, FloatProperty, StringProperty, EnumProperty

class EngSettings(PropertyCollection):
    def __init__(self, propDict=None):
        super().__init__()
        self.props['diameter'] = FloatProperty('Motor Diameter', 'm', 0, 1)
        self.props['length'] = FloatProperty('Motor Length', 'm', 0, 4)
        self.props['totalMass'] = FloatProperty('Total Mass', 'kg', 0, 1000)
        self.props['designation'] = StringProperty('Motor Designation')
        self.props['manufacturer'] = StringProperty('Motor Manufacturer')
        self.props['append'] = EnumProperty('Existing File', ['Append', 'Overwrite'])

        if propDict is not None:
            self.setProperties(propDict)

class engExportWidget(QWidget):

    newData = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_engExporterWidget()
        self.ui.setupUi(self)

        self.ui.widgetEngInfo.setPreferences(QApplication.instance().getPreferences())
        self.ui.pushButtonCancel.pressed.connect(self.hide)
        self.ui.pushButtonOk.pressed.connect(self.okPressed)

    def show(self):
        settings = EngSettings()
        self.ui.widgetEngInfo.loadProperties(settings)
        super().show()

    def okPressed(self):
        self.newData.emit(self.ui.widgetEngInfo.getProperties())
        self.hide()
