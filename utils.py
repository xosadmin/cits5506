import os
from datetime import datetime,timedelta
import uuid
import hashlib
import pytz
import random

def uuidGen():
    return str(uuid.uuid4())

def getTime(tz, switch=0):
    tz = pytz.timezone(tz)
    if switch == 1:
        timenow = datetime.now(tz).strftime("%d-%m-%Y")
    else:
        timenow = datetime.now(tz).strftime("%d/%m/%Y-%H:%M:%S")
    return timenow

def md5Calc(plainText):
    md5 = hashlib.md5()
    md5.update(plainText.encode('utf-8'))
    return str(md5.hexdigest())
