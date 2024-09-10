from flask_sqlalchemy import *
from utils import uuidGen,randomName
from flask_login import UserMixin

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    userID = db.Column(db.String(256), primary_key=True, default=uuidGen)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Pets(db.Model):
    __tablename__ = "pets"
    petID = db.Column(db.String(256), primary_key=True, default=uuidGen)
    petName = db.Column(db.String(80), nullable=False, default=randomName)