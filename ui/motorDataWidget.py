import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

from ui.views.MotorDataWidget_ui import Ui_MotorDataWidget
from lib.motor import MotorConfig, processRawData
from lib.logger import logger
from traceback import format_exc

class MotorDataWidget(QWidget):

    nextPage = pyqtSignal()
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MotorDataWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonNext.pressed.connect(self.nextPressed)
        self.ui.pushButtonBack.pressed.connect(self.back.emit)

    def setup(self, data):
        self.raw = {'time': [], 'force': [], 'pressure': []}
        rawFrames = []
        minTime = 0

        # Cut the data up into frames of the correct size
        for start in range(0, len(data), 16):
            rawFrames.append(data[start:start + 16])
        logger.log('Frames: {}'.format(len(rawFrames)))
        # Separate the frames into time, force, and pressure
        for frame in rawFrames:
            # Account for (16 bit) time looping around
            t = minTime + int(frame[0:2], 16) + (256 * int(frame[2:4], 16))
            if len(self.raw['time']) > 0 and t < self.raw['time'][-1]:
                minTime += 2 ** 16
                t += minTime
            self.raw['time'].append(t)
            self.raw['force'].append(int(frame[4:6], 16) + (int(frame[6:8], 16) << 8) + (int(frame[8:10], 16) << 16))
            self.raw['pressure'].append(int(frame[10:12], 16) + (int(frame[12:14], 16) << 8) + (int(frame[14:16], 16) << 16))

        self.ui.widgetTransducerSelector.reset()
        self.ui.motorData.setPreferences(QApplication.instance().getPreferences())
        self.ui.motorData.loadProperties(MotorConfig({'cutoffThreshold': 5}))

    def nextPressed(self):
        forceConv, pressConv = self.ui.widgetTransducerSelector.getConverters()
        if forceConv == None and pressConv == None:
            QApplication.instance().outputMessage('At least one transducer must be used.')
            logger.log('Both transducers set to "None", cancelling')
            return

        # TODO: Validate motor data object
        try:
            motorData = MotorConfig()
            motorData.setProperties(self.ui.motorData.getProperties())
            motor = processRawData(self.raw, forceConv, pressConv, motorData)
            QApplication.instance().newResult(motor)
            self.nextPage.emit()
        except Exception as err:
            QApplication.instance().outputException(err, 'Could not load motor')
            logger.error('Could not load motor. Error: {}'.format(format_exc()))
