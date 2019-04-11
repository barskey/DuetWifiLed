#################
#### imports ####
#################

from flask import render_template, request, redirect, url_for, flash, jsonify
import json
from . import setup_blueprint
from project.models import Settings
from project import db


################
#### routes ####
################

@setup_blueprint.route('/settings')
def settings():
    settings = json.load(open('pdlapp/settings.json'))
    rings = json.load(open('pdlapp/rings.json'))
    return render_template('setup/settings.html', settings=settings, rings=rings)

@setup_blueprint.route('/update_settings', methods=['GET', 'POST'])
def update_settings():
    settings = {
        'hostname': request.form.get('hostname'),
        'password': request.form.get('password'),
        'freq': request.form.get('freq'),
        'neo1pin': request.form.get('neo1pin'),
        'neo2pin': request.form.get('neo2pin'),
        'neo3pin': request.form.get('neo3pin'),
        'order': request.form.get('order')
    }

    with open('pdlapp/settings.json', 'w') as outfile:
        json.dump(settings, outfile)
    return jsonify({'msg': 'Settings saved.'})

def get_duet_status(type):
    settings = json.load(open('pdlapp/settings.json'))
    host = 'http://' + settings['hostname'] + '/rr_status'
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