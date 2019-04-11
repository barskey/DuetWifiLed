from flask import render_template, request, redirect, url_for
from flask import jsonify
import json
import requests
from pdlapp import app

@app.route('/')
@app.route('/index')
def index():
    settings = json.load(open('pdlapp/settings.json'))
    rings = json.load(open('pdlapp/rings.json'))
    return render_template('index.html', settings=settings, rings=rings)

@app.route('/update_settings', methods=['GET', 'POST'])
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

@app.route('/get_action_params', methods=['GET', 'POST'])
def get_action_params():
    rings = json.load(open('pdlapp/rings.json'))
    params = rings[request.form.get('ring')][request.form.get('event')]
    #print (params)
    return jsonify({'params': params})

@app.route('/update_action', methods=['GET', 'POST'])
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

def get_duet_status(type):
    settings = json.load(open('pdlapp/settings.json'))
    host = 'http://' + settings['hostname'] + '/rr_status'
    args = {'type': type}
    result = requests.post(host, json=args)
    print (result.text)
    return result.json()

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