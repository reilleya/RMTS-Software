import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt6.QtWidgets import QApplication

from pyFormGen.units import convertAll

POINT_COLOR = 'tab:blue'
LINE_COLOR = 'tab:red'

class CharacterizationGraphWidget(FigureCanvas):
    def __init__(self, parent):
        super(CharacterizationGraphWidget, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.preferences = None
        self.app = QApplication.instance()
        self.fit = None
        self.maxPressure = None

    def setPreferences(self, pref):
        self.preferences = pref

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

    def plotPoints(self, points):
        self.clear()

        xPoints = self.app.convertAllToUserUnits([point[0] for point in points], 'Pa')
        if len(xPoints) > 0:
            self.maxPressure = max(xPoints) * 1.5
        yPoints = convertAll([point[1] for point in points], 'm/s', self.app.getBurnRateUnit())

        self.axes.scatter(xPoints, yPoints, color=POINT_COLOR)
        self.axes.set_xlabel('Pressure ({})'.format(self.app.getUserUnit('Pa')))
        self.axes.set_ylabel('Burn Rate ({})'.format(self.app.getBurnRateUnit()))
        self.draw()

    def plotFit(self, a, n):
        if self.maxPressure is None:
            return
        fitPressures = np.linspace(0, self.maxPressure, num=1000)
        convA = self.app.convertBurnRateCoefficientToUserUnits(a, n)
        fitBurnrates = [convA * pressure ** n for pressure in fitPressures]

        self.fit = self.axes.plot(fitPressures, fitBurnrates, color=LINE_COLOR)
        self.draw()

    def displayStats(self, a, n, r):
        convA = self.app.convertBurnRateCoefficientToUserUnits(a, n)
        self.axes.set_title('$R_b = {:.4f} * {{P_c}}^{{{:.4f}}}$, $R^2$ = {:.6f}'.format(convA, n, r**2))
        self.draw()

    def clear(self):
        self.axes.clear()
        self.fit = None
        self.draw()

    def clearLine(self):
        if self.fit is not None:
            self.fit.remove()
            self.fit = None
