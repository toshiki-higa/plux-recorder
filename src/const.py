# >>> Set Constants
MAC_ADDRESS = "00:07:80:8C:0A:09"
SAMPLING_RATE  = 10 #Hz
LENGTH_DISPLAY = 30 #sec
INTERVAL = 1/SAMPLING_RATE * 2#sec
DURATION_KEEP_DATA = 30 #sec

# >>> Sensor Types
SENSOR_TYPES = {
    0: "UNKNOWN_CLASS",
    1: "EMG",
    2: "ECG",
    3: "LIGHT",
    4: "EDA",
    5: "BVP",
    6: "RESP",
    7: "XYZ",
    8: "SYNC",
    9: "EEG",
    10: "SYNC_ADAP",
    11: "SYNC_LED",
    12: "SYNC_SW",
    13: "USB",
    14: "FORCE",
    15: "TEMP",
    16: "VPROBE",
    17: "BREAKOUT",
    18: "OXIMETER",
    19: "GONI",
    20: "ACT",
    21: "EOG",
    22: "EGG",
    23: "ANSA",
    26: "OSL"
}