from matplotlib import pyplot as plt

def saveDatasheet(motorData, path, convertToUserAndFormat, convertAllToUserUnits, getUserUnit):
    forceAxes  = plt.subplot(211)
    pressureAxes = forceAxes.twinx()
    tableAxes = plt.subplot(212)

    forceAxes.grid(True)

    tableAxes.axis('off')
    tableFields = [
        ['Burn Time', convertToUserAndFormat(motorData.getBurnTime(), 's', 3)],
        ['Propellant Mass', convertToUserAndFormat(motorData.getPropMass(), 'kg', 3)]
    ]

    if motorData.hasForceConverter():
        forceAxes.set_title(motorData.getMotorDesignation(), fontdict={'fontsize': 18, 'fontweight': 'heavy'})
        forceAxes.plot(motorData.getTime(), convertAllToUserUnits(motorData.getForce(), 'N'), color = 'tab:blue')
        forceAxes.set_ylabel('Thrust ({})'.format(getUserUnit('N')))
        forceAxes.yaxis.label.set_color('tab:blue')
        tableFields += [
            ['Designation', motorData.getMotorDesignation()],
            ['Total Impulse', convertToUserAndFormat(motorData.getImpulse(), 'Ns', 1)],
            ['Specific Impulse', convertToUserAndFormat(motorData.getISP(), 's', 3)],
            ['Peak Thrust', convertToUserAndFormat(motorData.getPeakThrust(), 'N', 1)],
            ['Average Thrust', convertToUserAndFormat(motorData.getAverageThrust(), 'N', 1)]
        ]

    if motorData.hasPressureConverter():
        pressureAxes.plot(motorData.getTime(), convertAllToUserUnits(motorData.getPressure(), 'Pa'), color = 'tab:red')
        pressureAxes.set_ylabel('Pressure ({})'.format(getUserUnit('Pa')))
        pressureAxes.yaxis.label.set_color('tab:red')
        tableFields += [
            ['Peak Pressure', convertToUserAndFormat(motorData.getPeakPressure(), 'Pa', 3)],
            ['Average Pressure', convertToUserAndFormat(motorData.getAveragePressure(), 'Pa', 3)],
            ['Characteristic Velocity', convertToUserAndFormat(motorData.getCStar(), 'm/s', 3)]
        ]

    if motorData.hasForceConverter() and motorData.hasPressureConverter():
        tableFields.append(['Thrust Coefficient', str(round(motorData.getThrustCoefficient(), 3))])

    tableAxes.table(tableFields, loc='center')

    fig = plt.gcf()
    fig.set_size_inches(8.5, 11)

    plt.savefig(path)
    plt.close()
