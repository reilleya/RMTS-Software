HARDWARE_REVISIONS = {
    0: 'Revision 1.0',
    1: 'Revision 1.1',
    2: 'Revision 1.2',
    3: 'Revision 1.3'
}

def getHardwareRevisionString(versionNum):
    return HARDWARE_REVISIONS.get(versionNum, 'Unknown ({})'.format(versionNum))


def getFirmwareRevisionString(versionNum):
    return str(versionNum)