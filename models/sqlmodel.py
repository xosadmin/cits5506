from flask_sqlalchemy import *
from utils import uuidGen

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.String(256), primary_key=True, default=uuidGen)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
