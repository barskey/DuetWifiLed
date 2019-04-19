import threading
import requests
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')

db = SQLAlchemy()
db.init_app(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

handler = RotatingFileHandler('pi-duet-wifi.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

@app.before_first_request # this will get called before the first request, hence the start_runner loop to send a dummy request
def load_tasks():
    scheduler.add_job(func=get_status, trigger='interval', id='duet_status', seconds=5)

# hack to start background thread that polls localhost with request.
# this triggers the before_first_request decorator above so code runs automatically at application launch
def start_runner(app):
    def start_loop():
        not_started = True
        while not_started:
            logger.debug('::__init__:: In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/settings')
                if r.status_code == 200:
                    logger.info('::__init__:: Server started, quiting start_loop')
                    not_started = False
                logger.debug('::__init__:: Received status code:{}'.format(r.status_code))
            except:
                logger.debug('::__init__:: Server not yet started')
            time.sleep(2)

    logger.debug('::__init__:: Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()

start_runner(app)

from app import routes, models

# communication task for duet status
def get_status():
    response = None
    with app.app_context():
        s = Settings.query.first()
        host = 'http://' + s.hostname + '/rr_status'
        #print(host)
        host = 'http://localhost:5001/rr_status'
        args = {'type': '2'}
        response = requests.post(host, json=args)
        if response.status_code == requests.codes.ok:
            #printer.update_status(response.json())
            #update_rings()
            print('yay')
        #return result.json()

