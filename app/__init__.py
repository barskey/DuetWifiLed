import threading
import requests
import time
from flask import Flask
import sys

SIM_MODE = False

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

LOGFILE = 'pi-duet-wifi.log'
import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(LOGFILE, maxBytes=100000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

from flask_apscheduler import APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app.printer_status import PrinterStatus
printer = PrinterStatus()

#import board
#import neopixel
# Neopixel GLOBALS
#PIXEL_PIN = board.D18
PIXEL_PIN = None
NEO_PIXELS = 16 # number of pixels per neo-pixel ring
NUM_RINGS = 3   # How many neo-pixel rings will be connected in sequence
ORDER = 'RGB' #neopixel.RGB # pixel order (RGB, GRB, RGBW, GRBW)
pixels = None
#pixels = neopixel.NeoPixel(PIXEL_PIN, NEO_PIXELS * NUM_RINGS, brightness=0.2, auto_write=False, pixel_order=ORDER)

@app.before_first_request # this will get called before the first request, hence the start_runner loop to send a dummy request
def start_scheduler():
    logger.info('<-__init__-> Scheduling get_status job every 5s.')
    scheduler.add_job(func=get_duet_status, trigger='interval', id='duet_status', seconds=5)

# hack to start background thread that polls localhost with request.
# this triggers the before_first_request decorator above so code runs automatically at application launch
def start_runner(app):
    def start_loop():
        not_started = True
        while not_started:
            logger.debug('<-__init__-> In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/settings')
                if r.status_code == 200:
                    logger.info('<-__init__-> Server started, quiting start_loop')
                    not_started = False
                logger.debug('<-__init__-> Received local status code:{}'.format(r.status_code))
            except:
                logger.debug('<-__init__-> Server not yet started')
            time.sleep(2)

    logger.debug('<-__init__-> Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()

start_runner(app)

import json
from app import routes, models
from app.models import Settings, Param

# communication tasks for duet status
# gets type 3 status
def get_duet_status():
    if SIM_MODE is True:
        response = json.load(open('mockDuet/data.json'))
        printer.update_status(response)
        logger.debug('<-get_duet_status-> SIM_MODE:Printer status updated.')
        if printer.needs_update is True:
            logger.debug('<-get_duet_status-> SIM_MODE:Printer needs update. Running update_rings')
            update_rings()
            printer.needs_update = False
    else:
        response = None
        with app.app_context():
            s = Settings.query.first()
            host = 'http://' + s.hostname + '/rr_status'
            #print(host)
            #host = 'http://localhost:5001/rr_status'
            args = {'type': '3'}
            response = None
            try:
                response = requests.get(host, params=args)
            except:
                logger.debug('<-get_duet_status-> ***ERROR*** trying to get status host:{} args:{} response:{}'.format(host, args, sys.exc_info()[0]))
            if response is not None and response.status_code == 200:
                printer.update_status(response.json())
                logger.debug('<-get_duet_status-> Printer status updated.')
                if printer.needs_update is True:
                    logger.debug('<-get_duet_status-> Printer needs update. Running update_rings')
                    update_rings()
                    printer.needs_update = False


from app.actions import ActionThread

# LED actions
def update_rings():
    rings = {}
    with app.app_context():
        params = Param.query.all()
        # put results in organized dict object
        # TODO: Fix this double for-loop hack for converting param db query to usable dict object
        for p in params:
            rings[p.ringnum] = {}
        for p in params:
            rings[p.ringnum][p.event] = p.get_obj()

    for ring_num,events in rings.items():
        action_params = events[printer.get_event()] #  get params for action to take for current printer state
        t = printer.get_task(ring_num - 1)
        if t is not None:
            t.join()
        t = ActionThread(action_params, printer, pixels, ring_num)
        t.setName('ring{}'.format(ring_num))
        t.daemon = True
        t.start()
        printer.set_task(ring_num - 1, t)
