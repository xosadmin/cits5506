from flask import Blueprint, current_app, jsonify, request, render_template, url_for, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import and_
from models.sqlmodel import Users, Pets
from utils import uuidGen, commPrototype, getTime, md5Calc
from conf import sysinfo, mqttinfo
import logging

login_manager = LoginManager()
logger = logging.getLogger(__name__)
mainBluePrint = Blueprint('mainBluePrint', __name__)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

mqtt_data = {
    'waterlevel': None,
    'turbity': None,
    'weight': None
}

@mainBluePrint.route("/petinfo/<rfid>", methods=["GET"])
def getPetInfo(rfid):
    query = Pets.query.filter(Pets.rfid == rfid).first()
    if query:
        return jsonify({"petID": query.petID, "lastDrink": query.lastDrink})
    else:
        return jsonify({"error": "Pet not found"}), 404

@mainBluePrint.route("/manualactions/<action>", methods=["GET"])
def changewater(action):
    prototypeURL = sysinfo["prototypeAddr"]
    prototypePort = sysinfo["prototypePort"]
    route = ""
    if action == "changewater":
        route = "changewater"
    elif action == "waterrefill":
        route = "waterrefill"
    elif action == "resetfeeder":
        route = "resetfeeder"

    if route:
        resp = commPrototype(prototypeURL, prototypePort, route)
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
    return render_template('dashboard.html', mqtt_data=mqtt_data)

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
