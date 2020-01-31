class LowPass():
    def __init__(self, historyLength):
        self.maxSize = historyLength
        self._buffer = []

    def addData(self, data):
        self._buffer.append(data)
        if len(self._buffer) > self.maxSize:
            self._buffer.pop(0)
        return sum(self._buffer) / len(self._buffer)
