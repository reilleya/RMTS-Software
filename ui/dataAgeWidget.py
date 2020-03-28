from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import QTimer

class DataAgeWidget(QLineEdit):

    def __init__(self, parent):
        super().__init__()
        self.interval = 100
        self.timerValue = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.incrementTime)
        self.timer.setInterval(self.interval)

    def incrementTime(self):
        self.timerValue += self.interval
        self.updateText()

    def start(self):
        self.timer.start()

    def reset(self, restart = True):
        self.timerValue = 0
        self.timer.stop()
        self.updateText()
        if restart:
            self.timer.start()

    def updateText(self):
        self.setText('{}'.format(self.timerValue / 1000))
