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

def formatErrorMessage(device, code):
    if device in ERRORS and code in ERRORS[code]:
        message = ERRORS[device][code]
    else:
        message = "Unknown error."
    return "{}.{}: {}".format(device, code, message)
