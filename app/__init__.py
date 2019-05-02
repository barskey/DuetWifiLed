import threading
import requests
import time
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

from flask_apscheduler import APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app.printer_status import PrinterStatus
printer = PrinterStatus()

#import board
#import neopixel
#pixel_pin = board.D18
NEO_PIXELS = 16
NUM_RINGS = 3
ORDER = 'RGB' #neopixel.RGB
#pixels = neopixel.NeoPixel(pixel_pin, NEO_PIXELS * NUM_RINGS, brightness=0.2, auto_write=False, pixel_order=ORDER)

import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('pi-duet-wifi.log', maxBytes=100000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

@app.before_first_request # this will get called before the first request, hence the start_runner loop to send a dummy request
def load_tasks():
    logger.info('<-__init__-> Scheduling duet_status job every 5s.')
    scheduler.add_job(func=get_status, trigger='interval', id='duet_status', seconds=5)

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
                logger.debug('<-__init__-> Received status code:{}'.format(r.status_code))
            except:
                logger.debug('<-__init__-> Server not yet started')
            time.sleep(2)

    logger.debug('<-__init__-> Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()

start_runner(app)

from app import routes, models
from app.models import Settings, Param

# communication task for duet status
def get_status():
    response = None
    with app.app_context():
        s = Settings.query.first()
        host = 'http://' + s.hostname + '/rr_status'
        #print(host)
        host = 'http://localhost:5001/rr_status'
        args = {'type': '2'}
        try:
            response = requests.post(host, json=args)
            if response.status_code == requests.codes.ok:
                printer.update_status(response.json())
                logger.debug('<-get_status-> Printer staus updated.')
                if printer.needs_update is True:
                    logger.debug('<-get_status-> Printer needs update. Running update_rings')
                    update_rings()
        except:
            logger.debug('<-get_status-> error trying to get status host:{} args:{}'.format(host, args))
    #return response.json()

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
        settings = Settings.query.first()
        order = settings.order # TODO set ORDER as neopixel.RGB e.g.

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
        #print ('Ring {}: Do action {}!'.format(ring_num, action_num))
