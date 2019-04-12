from flask import Flask

######################################
#### Application Factory Function ####
######################################

def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates', static_folder='static')
    app.config.from_pyfile(config_filename)

    from project.models import db
    db.init_app(app)

    from project.setup import setup_blueprint
    app.register_blueprint(setup_blueprint)

    from project.ledcontrol import ledcontrol_blueprint
    app.register_blueprint(ledcontrol_blueprint)

    from project.comm import comm_blueprint
    app.register_blueprint(comm_blueprint)

    return app
