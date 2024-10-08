from flask_sqlalchemy import SQLAlchemy
from utils import uuidGen, randomName
from flask_login import UserMixin
from datetime import datetime
import pytz

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    userID = db.Column(db.String(256), primary_key=True, default=uuidGen)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def get_id(self):
        return str(self.userID)

class Pets(db.Model):
    __tablename__ = "pets"
    petID = db.Column(db.String(256), primary_key=True, default=uuidGen)
    petName = db.Column(db.String(80), nullable=False, default=randomName)
    weight = db.Column(db.Float, nullable=False, default=0.00)
    normalDrinkValue = db.Column(db.Float, nullable=False, default=0.00)
    lastTagDate = db.Column(db.String(100), nullable=False, default="None")

class PetDrink(db.Model):
    __tablename__ = "petdrink"
    eventID = db.Column(db.String(256), primary_key=True, default=uuidGen)
    petID = db.Column(db.String(256), db.ForeignKey("pets.petID"), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC))
    drinkAmount = db.Column(db.Float, nullable=False, default=0.00)

class noticeableEvent(db.Model):
    __tablename__ = "noticeEvent"
    eventID = db.Column(db.String(256), primary_key=True, default=uuidGen)
    petID = db.Column(db.String(256), db.ForeignKey("pets.petID"), nullable=False)
    eventType = db.Column(db.String(20), nullable=False, default="None")
    create_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC))
    eventCritical = db.Column(db.String(80), nullable=False, default="Notice")
    eventDetail = db.Column(db.String(120), nullable=False, default="None")
