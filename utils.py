import os
from datetime import datetime,timedelta
import uuid
import hashlib
import pytz
import random
import names
import urllib.request
from conf import barkList

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
    floatweight = float(weight)
    result = 40 * (floatweight ** 0.75)
    return f'{result:.2f}'

def sortEventSheet(query):
    result = [item.petID for item in query]
    return result

def barkPush(server,token,message):
    urlCompose = server + "/" + token + "/" + message + "?sound=tiptoes"
    f = urllib.request.urlopen(urlCompose)
    print(f.read())

def PushIOS(message):
    allUserList = []
    i = 0
    for values in barkList:
        allUserList.append(values)
    while i < len(allUserList):
        if "http" in allUserList[i]:
            if i + 1 < len(allUserList):
                barkPush(allUserList[i], allUserList[i+1], message)
            if i + 2 < len(allUserList):
                i += 2
            else:
                break
