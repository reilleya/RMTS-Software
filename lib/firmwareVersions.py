
ALLOWED_HARDWARE_REVISIONS = [2, 3]
ALLOWED_FIRMWARE_VERSIONS = [5]

def checkVersionPacket(packet):
    return packet.hardwareVersion in ALLOWED_HARDWARE_REVISIONS and packet.firmwareVersion in ALLOWED_FIRMWARE_VERSIONS