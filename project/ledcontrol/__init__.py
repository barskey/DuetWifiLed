"""
The setup Blueprint handles the NeoPixel ring params for this application.
"""
from flask import Blueprint
ledcontrol_blueprint = Blueprint('ledcontrol', __name__, template_folder='templates', static_folder='static', static_url_path='/ledcontrol/static')

from . import routes
