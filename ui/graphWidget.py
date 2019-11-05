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
        self.plot = self.figure.add_subplot(111)
        self.figure.tight_layout()

    def plotData(self, x, y):
        self.plot.clear()
        self.plot.plot(x, y)
        self.draw()
