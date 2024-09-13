from threading import Lock

mqtt_data = {
    'wastewaterlevel': None,
    'turbity_bowl': None,
    'valve': None,
    'weightBowl': None
}
mqtt_data_lock = Lock()
