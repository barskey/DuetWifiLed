"""
The setup Blueprint handles the NeoPixel ring params for this application.
"""
from flask import Blueprint
ledcontrol_blueprint = Blueprint('ledcontrol', __name__, template_folder='templates')

from . import routes
