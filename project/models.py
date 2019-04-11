from project import db
from datetime import datetime

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.String(30))
    password = db.Column(db.String(30))
    neo1pin = db.Column(db.Integer)
    neo2pin = db.Column(db.Integer)
    neo3pin = db.Column(db.Integer)
    freq = db.Column(db.Integer)
    order = db.Column(db.String(5))

class Param(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ringnum = db.Column(db.Integer)
    action = db.Column(db.Integer)
    event = db.Column(db.String(20))
    color1 = db.Column(db.String(8))
    color2 = db.Column(db.String(8))
    interval = db.Column(db.Integer)
