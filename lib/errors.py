ERRORS = {
    0: {
        0: "SD card nominal.",
        1: "No SD card detected.",
        2: "SD card unwritable. Please ensure it is formatted FAT32.",
        3: "SD card full.",
        255: "SD card uninitialized."
    },
    1: {
        0: "ADC nominal.",
        1: "ADC self-check failed.",
        255: "ADC uninitialized."
    },
    2: {
        0: "Radio nominal.",
        1: "Radio received malformed firing packet."
    }
}

def getErrorString(device, code):
    if device in ERRORS and code in ERRORS[code]:
        return ERRORS[device][code]
    return 'Unknown error.'

def getNominalString(device):
    return getErrorString(device, 0)

def formatErrorMessage(device, code):
    message = getErrorString(device, code)
    return "{}.{}: {}".format(device, code, message)
