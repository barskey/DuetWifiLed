#################
#### imports ####
#################

from flask import render_template, request, redirect, url_for, flash, jsonify
import json
from . import setup_blueprint
from project.models import db, Settings


################
#### routes ####
################

@setup_blueprint.route('/settings')
def settings():
    # TODO: There has to be a better way to check tables and init db with data
    db_init() #  add default vaules from file if table is empty

    settings = Settings.query.first()
    return render_template('setup/settings.html', settings=settings)

def db_init():
    #  if there's an error when trying to query, the tables probably need to be created
    try:
        Settings.query.all()
    except:
        db.create_all()
    
    if len(Settings.query.all()) == 0:
        defaults = json.load(open('project/settings.default.json'))
        s = Settings(
            hostname = defaults['hostname'],
            password = defaults['password'],
            neo1pin = defaults['neo1pin'],
            neo2pin = defaults['neo2pin'],
            neo3pin = defaults['neo3pin'],
            interval = defaults['interval'],
            order = defaults['order']
        )
        db.session.add(s)
        db.session.commit()

@setup_blueprint.route('/update_settings', methods=['GET', 'POST'])
def update_settings():
    s = Settings.query.first()
    s.hostname = request.form.get('hostname')
    s.password = request.form.get('password')
    s.interval = int(0 if request.form.get('interval') == '' else request.form.get('interval'))
    s.neo1pin = int(0 if request.form.get('neo1pin') == '' else request.form.get('neo1pin'))
    s.neo2pin = int(0 if request.form.get('neo2pin') == '' else request.form.get('neo2pin'))
    s.neo3pin = int(0 if request.form.get('neo3pin') == '' else request.form.get('neo3pin'))
    s.order = request.form.get('order')
    db.session.add(s)
    db.session.commit()
    return jsonify({'msg': 'Settings saved.'})
