#################
#### imports ####
#################

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
import json
from . import ledcontrol_blueprint
from project.models import db, Param


################
#### routes ####
################

@ledcontrol_blueprint.route('/')
@ledcontrol_blueprint.route('/index')
@ledcontrol_blueprint.route('/ledcontrol')
def ledcontrol():
    # TODO: There has to be a better way to check tables and init db with data
    db_init() #  add default vaules from file if table is empty

    # TODO: Fix this ungly hack for converting param db query to usable dict object
    params = Param.query.all()
    rings = {}
    for p in params:
        rings[p.ringnum] = {}
    for p in params:
        rings[p.ringnum][p.event] = p.get_obj()
    #print(rings)
    return render_template('ledcontrol/led.html', rings=rings)

def db_init():
    #  if there's an error when trying to query, the tables probably need to be created
    try:
        Param.query.all()
    except:
        db.create_all()
    
    if len(Param.query.all()) == 0:
        defaults = json.load(open('project/params.default.json'))
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

@ledcontrol_blueprint.route('/get_action_params', methods=['GET', 'POST'])
def get_action_params():
    params = Param.query.filter_by(ringnum=int(request.form.get('ring')), event=request.form.get('event')).first().get_obj()
    return jsonify({'params': params})

@ledcontrol_blueprint.route('/update_action', methods=['GET', 'POST'])
def update_action():
    params = Param.query.filter_by(ringnum=int(request.form.get('ring')), event=request.form.get('event')).first()
    params.action = int(request.form.get('action'))
    params.color1 = request.form.get('color1', 'rgb(0, 0, 0)')
    params.color2 = request.form.get('color2','rgb(0, 0, 0)')
    params.interval = int(request.form.get('interval'))
    db.session.add(params)
    db.session.commit()
    return jsonify({'msg': 'Action saved.'})
