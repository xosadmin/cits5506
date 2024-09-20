import os
from datetime import datetime,timedelta
import uuid
import hashlib
import pytz
import random
import names

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

def randomName():
    return names.get_full_name()

def calcNormalDrink(weight):
    result = 40 * (weight ** 0.75)
    return float(f'{result:.2f}')

def sortEventSheet(query):
    result = [item.petID for item in query]
    return result
