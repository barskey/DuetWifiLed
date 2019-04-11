"""
The setup Blueprint handles the DuetWifi communication setup for this application.
"""
from flask import Blueprint
setup_blueprint = Blueprint('setup', __name__, template_folder='templates')

from . import routes
