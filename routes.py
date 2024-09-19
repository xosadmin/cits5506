from flask import Blueprint, current_app, jsonify, request, render_template, url_for, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import and_,delete,update
from models.sqlmodel import *
from utils import uuidGen, getTime, md5Calc
from conf import sysinfo, mqttinfo
from models.mqtt import mqtt_data
from models.wificonn import wificonn
import logging
import paho.mqtt.client as mqtt

login_manager = LoginManager()
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
mqtt_client = mqtt.Client()
mainBluePrint = Blueprint('mainBluePrint', __name__)
timezone = pytz.timezone("Australia/Sydney")

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
@login_required
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

@mainBluePrint.route('/conn_data')
def conn_data_view():
    return jsonify(wificonn)

@mainBluePrint.route("/getpetdata/<petid>", methods=["GET"])
def getPetData(petid):
    query = Pets.query.filter(Pets.petID == petid).first()
    if query:
        result = {"Status":True,"PetID": petid, "PetName":query.petName}
    else:
        result = {"Status": False}
    return jsonify(result)

@mainBluePrint.route('/addpetdrink', methods=['POST'])
def submit_data():
    global timezone
    if request.is_json:
        data = request.get_json()
        eventID = uuidGen()
        date = datetime.now(timezone)
        petID = data.get('petID')
        drinkAmount = data.get('drinkAmount')
        try:
            query = PetDrink(eventID=eventID, create_date=date, petID=petID, drinkAmount=drinkAmount)
            db.session.add(query)
            db.session.execute(update(Pets).where(Pets.petID == petID).values(lastTagDate=datetime.now(timezone).strftime("%d/%m/%Y-%H:%M:%S")))
            db.session.commit()
            return jsonify({"Status": True, "Details": "Record updated."}), 200
        except Exception as e:
            print("Add Pet Drink Error: " + str(e))
            return jsonify({"Status": False, "Details": "Internal Error occurred."}), 400
    else:
        return jsonify({"Status": False, "Details": "Request must be in JSON format"}), 400
    
@mainBluePrint.route('/update_wificonn', methods=['POST'])
def update_wificonn():
    global timezone
    data = request.json
    wificonn['ipaddr'] = data.get('ipaddr', wificonn['ipaddr'])
    wificonn['rssi'] = data.get('rssi', wificonn['rssi'])
    wificonn['lastseen'] = datetime.now(timezone).strftime("%d/%m/%Y-%H:%M:%S")
    return jsonify({"Status": True, "Details": "Record updated."}), 200

@mainBluePrint.route('/update_sensordata', methods=['POST'])
def update_sensordata():
    data = request.json
    sensor = data.get('sensor', None)
    mqtt_data[sensor] = data.get('value', None)
    return jsonify({"Status": True, "Details": "Record updated."}), 200

# REST API handling end
# Below are handling GUI queries

@mainBluePrint.route("/dashboard")
@login_required
def dashboard():
    waterlevelpercentage = 0
    estimate_water_level_remain_days = 0
    return render_template('dashboard.html', 
                           mqtt_data=mqtt_data,
                           waterlevelpercentage=waterlevelpercentage,
                           estimate_water_level_remain_days=estimate_water_level_remain_days,
                           wificonn=wificonn)

@mainBluePrint.route("/petmgmt")
@login_required
def petmgmt():
    query = Pets.query.all()
    return render_template("petmgmt.html",result=query)

@mainBluePrint.route("/addpet", methods=["GET","POST"])
@login_required
def addPet():
    if request.method == "GET":
        return render_template("newpet.html")
    else:
        petID = request.form.get('petID', None)
        petName = request.form.get('petName', None)
        if petID and petName:
            try:
                query = Pets(petID=petID,petName=petName)
                db.session.add(query)
                db.session.commit()
                return "<script>alert('Pet registration successful.');window.location.href='/petmgmt';</script>"
            except Exception as e:
                print(f"Error during registration pet: {e}")
                return "<script>alert('System error occured.');window.location.href='/addpet';</script>"
        else:
            return "<script>alert('Invalid Argument.');window.location.href='/addpet';</script>"

@mainBluePrint.route("/delpet/<petid>", methods=["GET"])
@login_required
def delPet(petid):
    try:
        db.session.execute(delete(PetDrink).filter(PetDrink.petID == petid))
        db.session.execute(delete(Pets).filter(Pets.petID == petid))
        db.session.commit()
        return "<script>alert('Pet delete successful.');window.location.href='/petmgmt';</script>"
    except Exception as e:
        db.session.rollback()
        print(f"Error when delete pet: {e}")
        return "<script>alert('System error occured. Modification reverted.');window.location.href='/petmgmt';</script>"

@mainBluePrint.route("/drinkhistory")
@login_required
def drinkhistory():
    query = db.session.query(
        PetDrink.petID,
        Pets.petName,
        PetDrink.create_date,
        PetDrink.drinkAmount
    ).join(Pets, PetDrink.petID == Pets.petID).order_by(PetDrink.drinkAmount.desc()).all()
    return render_template("petdrinkhistory.html",result=query)

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
