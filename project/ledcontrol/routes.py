#################
#### imports ####
#################

from flask import render_template, request, redirect, url_for, flash, jsonify
import json
from . import ledcontrol_blueprint
from project.models import Param
from project import db


################
#### routes ####
################

@ledcontrol_blueprint.route('/')
@ledcontrol_blueprint.route('/index')
@ledcontrol_blueprint.route('/ledcontrol')
def ledcontrol():
    rings = json.load(open('pdlapp/rings.json'))
    return render_template('ledcontrol/led.html', rings=rings)

@ledcontrol_blueprint.route('/get_action_params', methods=['GET', 'POST'])
def get_action_params():
    rings = json.load(open('pdlapp/rings.json'))
    params = rings[request.form.get('ring')][request.form.get('event')]
    #print (params)
    return jsonify({'params': params})

@ledcontrol_blueprint.route('/update_action', methods=['GET', 'POST'])
def update_action():
    rings = json.load(open('pdlapp/rings.json'))
    rings[request.form.get('ring')][request.form.get('event')] = {
            'action': request.form.get('action'),
            'color1': request.form.get('color1', 'rgb(0, 0, 0)'),
            'color2': request.form.get('color2','rgb(0, 0, 0)'),
            'interval': request.form.get('interval', '')
        }
    with open('pdlapp/rings.json', 'w') as outfile:
        json.dump(rings, outfile)
    return jsonify({'msg': 'Action saved.'})
