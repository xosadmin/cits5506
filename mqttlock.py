from threading import Lock

mqtt_data = {
    'wastewaterlevel': None,
    'turbity_bowl': None,
    'turbity_watertank': None,
    'weight': None
}
mqtt_data_lock = Lock()
