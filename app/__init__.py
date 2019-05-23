import threading
import requests
import time
from flask import Flask
import sys

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')


from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

### Logger Init ###
import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(app.config['LOGFILE'], maxBytes=100000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

### Printer Init ###
from app.printer_status import PrinterStatus
printer = PrinterStatus()

### NeoPixel Init ###
import board
import neopixel
pixels = None
pixels = neopixel.NeoPixel(app.config['PIXEL_PIN'], app.config['NEO_PIXELS'] * app.config['NUM_RINGS'], auto_write=False, pixel_order=app.config['ORDER'])

### APScheduler Init ###
import json
from app import models, routes
from app.models import Settings, Param

from flask_apscheduler import APScheduler
from flask import session
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@scheduler.task('date', id='startup')
def startup():
    print('startup')
    with app.app_context():
        try:
            Settings.query.all()
        except:
            logger.info('<-startup-> ***ERROR*** Settings table not created yet.')
            logger.info('<-startup-> Dropping all db tables...')
            db.drop_all()
            logger.info('<-startup-> Creating all db tables...')
            db.create_all()
            
            logger.info('<-startup-> Adding default Settings values...')
            defaults = json.load(open('app/settings.default.json'))
            s = Settings(
                hostname = defaults['hostname'],
                password = defaults['password'],
                pixel_pin = defaults['pixel_pin'],
                interval = defaults['interval'],
                order = defaults['order'],
                num_pixels = defaults['num_pixels'],
                num_rings = defaults['num_rings']
            )
            db.session.add(s)
            db.session.commit()
            logger.info('<-startup-> Settings Done!')

            logger.info('<-startup-> Adding default Param values...')
            defaults = json.load(open('app/params.default.json'))
            for key,events in defaults.items():
                for event,param in events.items():
                    p = Param(
                        ringnum = int(key),
                        event = event,
                        action = param['action'],
                        color1 = param['color1'],
                        color2 = param['color2'],
                        interval = param['interval']
                    )
                    db.session.add(p)
            db.session.commit()
            logger.info('<-startup-> Done!')
        s = Settings.query.first()
        app.config['NEO_PIXELS'] = s.num_pixels
        app.config['NUM_RINGS'] = s.num_rings
        app.config['ORDER'] = neopixel.RGB
        if s.order == 'RGB':
            app.config['ORDER'] = neopixel.RGB
        elif s.order == 'RGBW':
            app.config['ORDER'] = neopixel.RGBW
        elif s.order == 'GRB':
            app.config['ORDER'] = neopixel.GRB
        elif s.order == 'GRBW':
            app.config['ORDER'] = neopixel.GRBW
        pixels.pixel_order = app.config['ORDER']
        
        app.config['PIXEL_PIN'] = board.D18
        if s.pixel_pin == 10:
            app.config['PIXEL_PIN'] = board.D10
        elif s.pixel_pin == 12:
            app.config['PIXEL_PIN'] = board.D12
        elif s.pixel_pin == 18:
            app.config['PIXEL_PIN'] = board.D18
        elif s.pixel_pin == 21:
            app.config['PIXEL_PIN'] = board.D21
        pixels.pixel_pin = app.config['PIXEL_PIN']

@scheduler.task('interval', id='duet_status', seconds=5)
def get_status():
    if app.config['SIM_MODE'] is True:
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
