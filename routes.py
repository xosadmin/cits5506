from flask import Blueprint, current_app, jsonify, request, render_template, url_for, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import and_
from models.sqlmodel import Users, Pets
from utils import uuidGen, getTime, md5Calc
from conf import sysinfo, mqttinfo
from mqttlock import mqtt_data
import logging
import paho.mqtt.client as mqtt

login_manager = LoginManager()
logger = logging.getLogger(__name__)
mqtt_client = mqtt.Client()
mainBluePrint = Blueprint('mainBluePrint', __name__)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

def mqtt_connect():
    try:
        mqtt_client.connect(mqttinfo['brokerAddr'], mqttinfo['port'], 60)
        mqtt_client.loop_start()
        print("MQTT connected")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")

def send_mqtt_message(topic, payload):
    mqtt_connect()
    result = mqtt_client.publish(topic, payload)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        return False
    else:
        return True

@mainBluePrint.route("/petinfo/<rfid>", methods=["GET"])
def getPetInfo(rfid):
    query = Pets.query.filter(Pets.rfid == rfid).first()
    if query:
        return jsonify({"petID": query.petID, "lastDrink": query.lastDrink})
    else:
        return jsonify({"error": "Pet not found"}), 404

@mainBluePrint.route("/manualactions/<action>", methods=["GET"])
def changewater(action):
    route = ""
    if action == "changewater":
        route = "changewater"
    elif action == "refillwater":
        route = "refillwater"
    elif action == "restartfeeder":
        route = "restartfeeder"
    if route:
        resp = send_mqtt_message("remotecommand",route)
        if resp:
            return jsonify({"Status": True, "Details": "Command successfully sent"})
        else:
            return jsonify({"Status": False, "Details": "Cannot connect to prototype"})
    else:
        return jsonify({"Status": False, "Details": "Invalid action"}), 400

@mainBluePrint.route('/mqtt_data')
def mqtt_data_view():
    return jsonify(mqtt_data)

# REST API handling end
# Below are handling GUI queries

@mainBluePrint.route("/dashboard")
@login_required
def dashboard():
    if mqtt_data.get('turbity_bowl') is None or mqtt_data.get('turbity_bowl') <= 0.25:
        turbBowl = "Low"
    else:
        turbBowl = "High"
    if mqtt_data.get('turbity_watertank') is None or mqtt_data.get('turbity_watertank') <= 0.25:
        turbWt = "Low"
    else:
        turbWt = "High"
    return render_template('dashboard.html', mqtt_data=mqtt_data,turbBowl=turbBowl,turbWt=turbWt)

@mainBluePrint.route("/petmgmt")
@login_required
def petmgmt():
    render_template("petmgmt.html")

@mainBluePrint.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

@mainBluePrint.route("/", methods=["GET", "POST"])
@mainBluePrint.route("/login", methods=["POST"])
def defaultReturn():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        if username and password:
            hashedPassword = md5Calc(password)
            query = Users.query.filter(and_(Users.username == username, Users.password == hashedPassword)).first()

            if query:
                login_user(query)
                return redirect(url_for("mainBluePrint.dashboard"))
            else:
                return "<script>alert('Wrong username or password!');window.location.href='/';</script>"
        else:
            return "<script>alert('Invalid Parameter!');window.location.href='/';</script>"
