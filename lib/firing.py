from PyQt5.QtCore import QObject, pyqtSignal

PACKET_STRIDE = 10

class Firing(QObject):
    """Contains the results of a single firing """

    newGraph = pyqtSignal(list, list, list)

    def __init__(self):
        super().__init__()
        self.origin = 'radio'
        self.rawData = {}
        self.startIndex = None
        self.lastSend = 0

    def processRawData(self):
        t = []
        f = []
        p = []

        recv = list(self.rawData.keys())
        recv.sort()
        for i in recv:
            t.append(self.rawData[i].time)
            f.append(self.rawData[i].force)
            p.append(self.rawData[i].pressure)

        f = [(d - 105000) * 70 / 390000 for d in f]

        t = [d / 1000 for d in t]
        f = [d * 4.448 for d in f]
        p = [d for d in p]

        maxForce = max(f)
        endCutoff = f.index(maxForce)
        while f[endCutoff] > 0.05 * maxForce:
            endCutoff += 1
        endCutoff = min(endCutoff + 10, len(f))

        t, f, p = t[:endCutoff], f[:endCutoff], p[:endCutoff]

        startCutoff = f.index(maxForce)
        while f[startCutoff] > 0.05 * maxForce:
            startCutoff -= 1
        endCutoff = max(startCutoff - 15, 0)

        t, f, p = t[startCutoff:], f[startCutoff:], p[startCutoff:]

        burnTime = t[-1] - t[0]
        startupTransient = t[0]
        print('Burn Time: {} s'.format(round(burnTime, 3)))
        print('Startup Transient: {} s'.format(round(startupTransient, 3)))
        t = [d - t[0] for d in t]

        totalImpulse = 0
        for i in range(1, len(t)):
            totalImpulse += (t[i] - t[i -1 ]) * (f[i] + f[i - 1]) / 2
        print('Total Impulse: {} Ns'.format(round(totalImpulse, 3)))
        averageForce = sum(f) / len(f)
        print('Average Force: {} N'.format(round(averageForce, 3)))
        print()

        return t, f, p

    def addDatapoint(self, packet):
        self.rawData[packet.seqNum] = packet
        if len(self.rawData) == 1:
            self.startIndex = packet.seqNum
        elif abs(packet.seqNum - self.startIndex) < PACKET_STRIDE:
            if len(self.rawData) > self.lastSend:
                t, f, p = self.processRawData()
                self.lastSend = len(self.rawData)
                self.newGraph.emit(t, f, p)
