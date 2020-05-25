def migrateFiring_0_1_0_to_0_2_0(data):
    data['motorInfo']['cutoffThreshold'] = 5
    return data
