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
    s.interval = int(request.form.get('interval'))
    s.neo1pin = int(request.form.get('neo1pin'))
    s.neo2pin = int(request.form.get('neo2pin'))
    s.neo3pin = int(request.form.get('neo3pin'))
    s.order = request.form.get('order')
    db.session.add(s)
    db.session.commit()
    return jsonify({'msg': 'Settings saved.'})

def get_duet_status(type):
    s = Settings.query.first()
    host = 'http://' + s.hostname + '/rr_status'
    args = {'type': type}
    #result = requests.post(host, json=args)
    #print (result.text)
    #return result.json()

def solid_color(color, order):
    # color is rgb(#, #, #)
    rgb = color[4:-1].split(',')
    r = rgb[0].strip()
    g = rgb[1].strip()
    b = rgb[2].strip()
    if order == "RGB":
        #pixels.fill((r,g,b))
        pass
    else:
        #pixels.fill((g,r,b))
        pass
    #pixels.show()