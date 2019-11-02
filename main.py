import time
from lib.radio import RadioManager

import sys
from app import App
from PyQt5.QtCore import Qt

# Hide the hi-dpi switch behind a platform check
# Works on Windows, unneccessary on macOS, and breaks GNOME
# cf. https://github.com/reilleya/openMotor/pull/103#issuecomment-513507028
if sys.platform == 'win32':
    # must be set before the app is constructed
    # cf. https://doc.qt.io/qt-5/highdpi.html
    # and https://www.riverbankcomputing.com/static/Docs/PyQt5/api/qtcore/qt.html#ApplicationAttribute
    App.setAttribute(Qt.AA_EnableHighDpiScaling)

app = App(sys.argv)
sys.exit(app.exec())


"""rm = RadioManager('/dev/ttyUSB0')
rm.run()

time.sleep(5)
for i in range(0, 5):
    rm.sendPacket(128, 0, [0x10, 0x27, 0xFF, 0x01, 0, 0, 0, 0])
    time.sleep(0.05)


def animate(i):
    global lastLen
    if len(rm.results) > 10 and len(rm.results) > lastLen:
        lastLen = len(rm.results)
        x = []
        y = []
        recv = list(rm.results.keys())
        recv.sort()
        for p in recv:
            x.append(rm.results[p].time)
            y.append((rm.results[p].force - 110000) * 70 / 390000)
        ax.clear()
        plt.title('{}/1000'.format(len(rm.results)))
        ax.plot(x, y)

import matplotlib.pyplot as plt
import matplotlib.animation as animation

lastLen = 0

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ani = animation.FuncAnimation(fig, animate, interval=250)
plt.show()"""


