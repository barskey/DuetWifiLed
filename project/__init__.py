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

    scheduler.init_app(app)
    scheduler.start()
    
    from project.setup import setup_blueprint
    app.register_blueprint(setup_blueprint)

    from project.ledcontrol import ledcontrol_blueprint
    app.register_blueprint(ledcontrol_blueprint)

    @app.before_first_request
    def load_tasks():
        from project.tasks import get_status

    start_runner()

    return app

# hack to start background thread that polls localhost with request.
# this triggers the before_first_request decorator above so code runs automatically at application launch
def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/')
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()
