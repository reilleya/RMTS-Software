import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication

FORCE_COLOR = 'tab:blue'
PRESSURE_COLOR = 'tab:red'

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

    def convertAndPlot(self, time, force=None, pressure=None, gridLines=False):
        app = QApplication.instance()
        if force is not None:
            force = app.convertAllToUserUnits(force, 'N')
        if pressure is not None:
            pressure = app.convertAllToUserUnits(pressure, 'Pa')
        self.plotData(time, force, pressure, gridLines)
        self.forceAxes.set_xlabel('Time (s)')
        if force is not None:
            self.forceAxes.set_ylabel('Force ({})'.format(app.getUserUnit('N')))
            self.forceAxes.yaxis.label.set_color(FORCE_COLOR)
        if pressure is not None:
            self.pressureAxes.set_ylabel('Pressure ({})'.format(app.getUserUnit('Pa')))
            self.pressureAxes.yaxis.label.set_color(PRESSURE_COLOR)
        self.draw()

    def plotData(self, time, force=None, pressure=None, gridLines=False):
        self.forceAxes.clear()
        self.pressureAxes.clear()
        if force is not None:
            self.forceAxes.plot(time, force, color=FORCE_COLOR)
        if pressure is not None:
            self.pressureAxes.plot(time, pressure, color=PRESSURE_COLOR)
        self.forceAxes.relim()
        self.forceAxes.autoscale()
        self.forceAxes.set_ylim(bottom=0)
        self.forceAxes.grid(gridLines)
        self.pressureAxes.relim()
        self.pressureAxes.autoscale()
        self.pressureAxes.set_ylim(bottom=0)
        self.draw()

    def clear(self):
        self.forceAxes.clear()
        self.pressureAxes.clear()
        self.draw()
