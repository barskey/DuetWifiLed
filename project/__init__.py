import threading
import requests
import time
from flask import Flask
from flask_apscheduler import APScheduler

######################################
#### Application Factory Function ####
######################################

scheduler = APScheduler()

def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates', static_folder='static')
    app.config.from_pyfile(config_filename)

    from project.models import db
    db.init_app(app)

    from project.printer_status import PrinterStatus
    app.printer = PrinterStatus()

    setup_logging(app)
    setup_scheduler(app)
    register_blueprints(app)

    @app.before_first_request # this will get called before the first request, hence the start_runner loop to send a dummy request
    def load_tasks():
        from project.tasks import get_status

    start_runner(app)

    return app

def setup_logging(app):
    import logging
    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler('pi-duet-wifi.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

def setup_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
    
def register_blueprints(app):
    from project.setup import setup_blueprint
    app.register_blueprint(setup_blueprint)

    from project.ledcontrol import ledcontrol_blueprint
    app.register_blueprint(ledcontrol_blueprint)

# hack to start background thread that polls localhost with request.
# this triggers the before_first_request decorator above so code runs automatically at application launch
def start_runner(app):
    def start_loop():
        not_started = True
        while not_started:
            app.logger.debug('::__init__:: In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/settings')
                if r.status_code == 200:
                    app.logger.info('::__init__:: Server started, quiting start_loop')
                    not_started = False
                app.logger.debug('::__init__:: Received status code:{}'.format(r.status_code))
            except:
                app.logger.debug('::__init__:: Server not yet started')
            time.sleep(2)

    app.logger.debug('::__init__:: Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()
