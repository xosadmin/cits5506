from flask import Flask
from conf import dbinfo, mqttinfo
from models.sqlmodel import db
from utils import uuidGen
from routes import mainBluePrint, mqtt_data, login_manager
import logging
import paho.mqtt.client as mqtt
import threading
from models.mqtt import mqtt_data,mqtt_data_lock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT Connection callback
def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT Status: {rc}")
    if rc == 0:
        logger.info("MQTT connected successfully")
        client.subscribe("sensor/waterlevel/waste")
        client.subscribe("sensor/TurbiditySensor_Bowl")
        client.subscribe("sensor/valve")
        client.subscribe("sensor/wasteTank")
        client.subscribe("sensor/weightBowl")
    else:
        logger.error(f"MQTT connection failed with status code {rc}")

def on_message(client, userdata, msg):
    global mqtt_data
    with mqtt_data_lock:
        if msg.topic == "sensor/wastewaterlevel":
            mqtt_data['wastewaterlevel'] = msg.payload.decode()
        elif msg.topic == "sensor/TurbiditySensor_Bowl":
            mqtt_data['turbity_bowl'] = msg.payload.decode()
        elif msg.topic == "sensor/valve":
            mqtt_data['valve'] = msg.payload.decode()
        elif msg.topic == "sensor/weightBowl":
            mqtt_data['weightBowl'] = msg.payload.decode()
    print(f"Received MQTT message on {msg.topic}: {msg.payload.decode()}")

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(mqttinfo["brokerAddr"], mqttinfo["port"], 60)
        client.loop_forever()
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")

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
