# Didn't want to pull in oM as a dependency, so this is a bit hacky
def getOpenMotorFileString(name, density, a, n, maxPressure, minPressure, k, m, t):
	return """data:
  config:
    ambPressure: 101324.99674500001
    burnoutThrustThres: 0.1
    burnoutWebThres: 2.5400050800101604e-05
    flowSeparationWarnPercent: 0.05
    mapDim: 750
    maxMassFlux: 1406.4697609001405
    maxPressure: 10342500.000000002
    minPortThroat: 2.0
    sepPressureRatio: 0.4
    timestep: 0.03
  grains: []
  nozzle:
    convAngle: 0.0
    divAngle: 0.0
    efficiency: 0.0
    erosionCoeff: 0.0
    exit: 0.0
    slagCoeff: 0.0
    throat: 0.0
    throatLength: 0.0
  propellant:
    density: {}
    name: {}
    tabs:
    - a: {}
      k: {}
      m: {}
      maxPressure: {}
      minPressure: {}
      n: {}
      t: {}
type: !!python/object/apply:uilib.fileIO.fileTypes
- 3
version: !!python/tuple
- 0
- 6
- 0""".format(density, name, a, k, m, maxPressure, minPressure, n, t)
