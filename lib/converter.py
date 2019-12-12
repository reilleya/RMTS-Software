
class Converter():
    def __init__(self, forceOffset, forceRatio, pressureOffset, pressureRatio):
        self.forceOffset = forceOffset
        self.forceRatio = forceRatio
        self.pressureOffset = pressureOffset
        self.pressureRatio = pressureRatio

    def forceToRaw(self, force):
        return (force - self.forceOffset) / self.forceRatio

    def convertForce(self, force):
        return self.forceRatio * force + self.forceOffset

    def convertPressure(self, pressure):
        return self.pressureRatio * pressure + self.pressureOffset

    def convertForces(self, forces):
        return [self.convertForce(f) for f in forces]

    def convertPressures(self, pressures):
        return [self.convertPressure(p) for p in pressures]

    @staticmethod
    def fromDictionary(d):
        return Converter(d['forceOffset'], d['forceRatio'], d['pressureOffset'], d['pressureRatio'])

    def toDictionary(self):
        return {
            'forceOffset': self.forceOffset,
            'forceRatio': self.forceRatio,
            'pressureOffset': self.pressureOffset,
            'pressureRatio': self.pressureRatio
        }
