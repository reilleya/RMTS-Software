import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GraphWidget(FigureCanvas):
    def __init__(self, parent):
        super(GraphWidget, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.preferences = None

    def setPreferences(self, pref):
        self.preferences = pref

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.forceAxes = self.figure.add_subplot(111)
        self.pressureAxes = self.forceAxes.twinx()
        self.figure.tight_layout()

    def plotData(self, x, y, y2 = None):
        self.forceAxes.clear()
        self.pressureAxes.clear()
        self.forceAxes.plot(x, y, color='tab:blue')
        if y2 is not None:
            self.pressureAxes.plot(x, y2, color='tab:red')
        self.draw()
