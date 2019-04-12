"""
The setup Blueprint handles the communication with the Duet Wifi for this application.
"""
from flask import Blueprint
comm_blueprint = Blueprint('comm', __name__)
from apscheduler.schedulers.background import BackgroundScheduler

from . import comm

scheduler = BackgroundScheduler()
scheduler.add_job(comm.get_status, 'interval', args=('2'), minutes=1, id="duet_status")
scheduler.start()