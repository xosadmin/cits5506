import os
from flask import Flask
from conf import dbinfo,mqttinfo
from models.sqlmodel import db
from utils import uuidGen
from routes import mainBluePrint, mqtt_data
import logging
import paho.mqtt.client as mqtt
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT 连接回调函数
def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT Status: {rc}")
    client.subscribe("sensors/waterlevel")
    client.subscribe("sensors/turbity")
    client.subscribe("sensors/weight")

def on_message(client, userdata, msg):
    global mqtt_data
    if msg.topic == "sensors/waterlevel":
        mqtt_data['waterlevel'] = msg.payload.decode()
    elif msg.topic == "sensors/turbity":
        mqtt_data['turbity'] = msg.payload.decode()
    elif msg.topic == "sensors/weight":
        mqtt_data['weight'] = msg.payload.decode()

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqttinfo["brokerAddr"], mqttinfo["port"], 60)
    client.loop_forever()

def create_app():
    app = Flask(__name__)
    try:
        db_uri = f"mysql+pymysql://{dbinfo['username']}:{dbinfo['password']}@" \
                 f"{dbinfo['server']}:{dbinfo['port']}/{dbinfo['dbname']}"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SECRET_KEY'] = uuidGen()
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        raise
    db.init_app(app)
    app.register_blueprint(mainBluePrint)
    return app

def start_mqtt_thread():
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.start()

app = create_app()

if __name__ == '__main__':
    start_mqtt_thread()
    app.run(debug=True)
