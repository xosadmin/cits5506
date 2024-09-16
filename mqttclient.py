from conf import mqttinfo
from models.mqtt import mqtt_data
from models.wificonn import wificonn
import paho.mqtt.client as mqtt
import logging
import time
import requests

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_sensor_data(topic,value):
    try:
        dataCompose = {
            "sensor": topic,
            "value": value
        }
        response = requests.post("http://203.29.240.135:5000/update_sensordata", json=dataCompose)
        if response.status_code == 200:
            print("Data sent successfully to the API")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to the API: {e}")

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    if msg.topic == "waterlevelwaste":
        update_sensor_data("wastewaterlevel",data)
    elif msg.topic == "turbiditysensor":
        update_sensor_data("turbity_bowl",data)
    elif msg.topic == "valve":
        update_sensor_data("valve",data)
    elif msg.topic == "weightbowl":
        update_sensor_data("weightBowl",data)
    logger.info(f"Received MQTT message on {msg.topic}: {data}")

def on_connect(client, userdata, flags, rc):
    print(f"MQTT Status: {rc}")
    if rc == 0:
        client.subscribe("waterlevelwaste")
        client.subscribe("turbiditysensor")
        client.subscribe("valve")
        client.subscribe("weightbowl")
    else:
        print("Error during on_connect")

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(mqttinfo["brokerAddr"], mqttinfo["port"])
        print("Connected to MQTT Broker.")
        client.loop_forever()
    except Exception as e:
        time.sleep(5)
        start_mqtt()
