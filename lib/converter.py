from pyFormGen.properties import PropertyCollection, StringProperty, FloatProperty, EnumProperty
from enum import Enum

class ConverterType(Enum):
    LOAD_CELL = 0
    PRESSURE_TRANSDUCER = 1

class BaseConverter(PropertyCollection):
    def __init__(self, propDict=None):
        super().__init__()
        self.props['name'] = StringProperty('Name')
        self.props['type'] = EnumProperty('Type', ['Load Cell', 'Pressure Transducer'])

class Converter(BaseConverter):
    def __init__(self, propDict=None):
        super().__init__()
        self.props['ratio'] = FloatProperty('Ratio', '', -1e10, 1e10)
        self.props['offset'] = FloatProperty('Offset', '', -1e10, 1e10)

        if propDict is not None:
            self.setProperties(propDict)

    def convert(self, reading):
        return self.getProperty('ratio') * reading + self.getProperty('offset')

    def toRaw(self, value):
        return (value - self.getProperty('offset')) / self.getProperty('ratio')

    def convertMultiple(self, readings):
        return [self.convert(r) for r in readings]
