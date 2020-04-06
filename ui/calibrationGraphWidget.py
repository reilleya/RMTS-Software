import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication

POINT_COLOR = 'tab:blue'
LINE_COLOR = 'tab:red'

class CalibrationGraphWidget(FigureCanvas):
    def __init__(self, parent):
        super(CalibrationGraphWidget, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.preferences = None
        self.app = QApplication.instance()
        self.fit = None

    def setPreferences(self, pref):
        self.preferences = pref

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

    def plotPoints(self, points):
        self.clear()
        self.axes.scatter(points[0], self.app.convertAllToUserUnits(points[1], self.baseUnit), color=POINT_COLOR)
        self.axes.set_xlabel('Raw counts')
        self.axes.set_ylabel('{} ({})'.format(self.label, self.app.getUserUnit(self.baseUnit)))
        self.draw()

    def plotLine(self, points):
        self.fit = self.axes.plot(points[0], self.app.convertAllToUserUnits(points[1], self.baseUnit), color=LINE_COLOR)
        self.draw()

    def displayR(self, r):
        self.axes.set_title('R-squared = {}'.format(r**2))
        self.draw()

    def clear(self):
        self.axes.clear()
        self.fit = None
        self.draw()

    def clearLine(self):
        if self.fit is not None:
            self.fit.remove()
            self.fit = None

    def setUnit(self, label, unit):
        self.label = label
        self.baseUnit = unit
