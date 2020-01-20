from enum import Enum

class ConverterType(Enum):
    LOAD_CELL = 0
    PRESSURE_TRANSDUCER = 1

class Converter():

    TYPES = {}

    def __init__(self, transducer, offset, ratio):
        self.transducer = transducer
        self.offset = offset
        self.ratio = ratio

    def convert(self, force):
        return self.ratio * force + self.offset

    def toRaw(self, force):
        return (force - self.offset) / self.ratio

    def convertMultiple(self, readings):
        return [self.convert(r) for r in readings]

    @staticmethod
    def fromDictionary(d):
        return Converter(d['type'], d['offset'], d['ratio'])

    def toDictionary(self):
        return {
            'type': self.transducer,
            'offset': self.forceRatio,
            'ratio': self.pressureOffset,
        }
