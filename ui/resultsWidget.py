import sys
from PyQt5.QtWidgets import QWidget

from ui.views.ResultsWidget_ui import Ui_ResultsWidget

from lib.firing import Firing

class ResultsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)

        self.firing = None

        self.reset()

    def processResultsPacket(self, packet):
        if self.firing is not None: 
            self.firing.addDatapoint(packet)

    def onFireButtonPressed(self):
        fireData = self.ui.widgetFiringConfig.getProperties()
        # Validate fire object
        self.beginFire.emit(fireData)

    def reset(self):
        self.firing = Firing()
        self.firing.newGraph.connect(self.showResults)

    def showResults(self, time, force, pressure):
        self.ui.widgetGraph.plotData(time, force)
