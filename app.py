from flask import Flask
import time
from conf import dbinfo, mqttinfo
from models.sqlmodel import db
from utils import uuidGen
from routes import mainBluePrint, login_manager
import paho.mqtt.client as mqtt
import threading
import logging
import requests

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MQTT Connection callback
def on_connect(client, userdata, flags, rc):
    print(f"MQTT Status: {rc}")
    if rc == 0:
        app.logger.info("MQTT connected successfully")
        client.subscribe("waterlevelwaste")
        client.subscribe("turbiditysensor")
        client.subscribe("valve")
        client.subscribe("weightbowl")
    else:
        app.logger.info(f"MQTT connection failed with status code {rc}")

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


def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(mqttinfo["brokerAddr"], mqttinfo["port"])
        print("Connected to MQTT Broker.")
        client.loop_forever()
    except Exception as e:
        app.logger.info(f"Failed to connect to MQTT broker: {e}")
        time.sleep(5)
        start_mqtt()

def create_app():
    app = Flask(__name__)
    try:
        db_uri = f"mysql+pymysql://{dbinfo['username']}:{dbinfo['password']}@" \
                 f"{dbinfo['server']}:{dbinfo['port']}/{dbinfo['dbname']}"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SECRET_KEY'] = uuidGen()
        app.logger.setLevel(logging.INFO)
    except Exception as e:
        app.logger.info(f"Failed to create app: {e}")
        raise
    db.init_app(app)
    app.register_blueprint(mainBluePrint)
    login_manager.init_app(app)  # Initialize the login manager
    login_manager.login_view = "mainBluePrint.defaultReturn"  # Default login view
    return app

def start_mqtt_thread():
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True  # Set thread as daemon so it exits when the main thread does
    mqtt_thread.start()

app = create_app()

if __name__ == '__main__':
    start_mqtt_thread()
    app.run(debug=True)
