from app import db
from datetime import datetime

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.String(30))
    password = db.Column(db.String(30))
    pixel_pin = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    order = db.Column(db.String(5))
    num_pixels = db.Column(db.Integer)
    num_rings = db.Column(db.Integer)
    loglevel = db.Column(db.String(10))

    def __repr__(self):
        return 'hostname:{}'.format(self.hostname)

class Param(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ringnum = db.Column(db.Integer)
    action = db.Column(db.Integer)
    event = db.Column(db.String(20))
    color1 = db.Column(db.String(8))
    color2 = db.Column(db.String(8))
    interval = db.Column(db.Float, nullable=True)

    def get_obj(self):
        return {
            'action': self.action,
            'color1': self.color1,
            'color2': self.color2,
            'interval': self.interval
        }

    def __repr__(self):
        return 'Ring {}: {}/{}'.format(self.ringnum, self.event, self.action)
