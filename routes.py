import os
from operator import and_
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import *
from werkzeug.utils import secure_filename
from models.sqlmodel import *
from utils import uuidGen
from conf import sysinfo
import logging

logger = logging.getLogger(__name__)
mainBluePrint = Blueprint('mainBluePrint', __name__)

@mainBluePrint.route("/")
def defaultReturn():
    return jsonify({"Status": False, "Details": "Route is not defined."})
