from flask import render_template, request, redirect, url_for
from flask import jsonify
import json
import requests
from pdlapp import app

@app.route('/')
@app.route('/index')
def index():
    settings = json.load(open('pdlapp/settings.json'))
    return render_template('index.html', settings=settings)

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

def get_status(type):
    settings = json.load(open('pdlapp/settings.json'))
    host = 'http://' + settings['hostname'] + '/rr_status'
    args = {'type': type}
    result = requests.post(host, json=args)
    print (result.text)
    return result.json()