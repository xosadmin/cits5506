import os
from operator import and_
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import *
from werkzeug.utils import secure_filename
from models.sqlmodel import *
from utils import uuidGen, commPrototype, getTime, md5Calc
from conf import sysinfo, mqttinfo
import logging

logger = logging.getLogger(__name__)
mainBluePrint = Blueprint('mainBluePrint', __name__)

mqtt_data = {
    'waterlevel': None,
    'turbity': None,
    'weight': None
}

@mainBluePrint.route("/petinfo/<rfid>",methods=["GET"])
def getPetInfo(rfid):
    query = Pets.query.filter(Pets.rfid == rfid).first()
    petID = query.petID
    lastDrink = query.lastDrink
    return jsonify({"petID": petID, "lastDrink": lastDrink})

@mainBluePrint.route("/manualactions/<action>",methods=["GET"])
def changewater(action):
    prototypeURL = sysinfo["prototypeAddr"]
    prototypePort = sysinfo["prototypePort"]
    if action == "changewater":
        route = "changewater"
    elif action == "waterrefill":
        route = "waterrefill"
    resp = commPrototype(prototypeURL,prototypePort,route)
    if resp:
        return jsonify({"Status": True, "Details": "Command successfully sent"})
    else:
        return jsonify({"Status": False, "Details": "Cannot connect to prototype"})

@mainBluePrint.route("/")
def defaultReturn():
    return jsonify({"Status": False, "Details": "Route is not defined."})
