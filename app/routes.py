from app import app, db, logger, printer, pixels
from flask import render_template, redirect, url_for, request, jsonify
import json
import requests, sys
import logging
from app.models import Settings, Param
from app.actions import ActionThread
import neopixel
import board

@app.context_processor
def context_processor():
    # if Settings can't be queried, reset to defaults to create tables and load defaults
    try:
        Settings.query.all()
    except:
        return redirect('/reset_to_defaults')

    settings = Settings.query.first()
    return dict(simmode=app.config['SIM_MODE'], settings=settings)

###########################
####    setup routes   ####
###########################

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/update_settings', methods=['GET', 'POST'])
def update_settings():
    s = Settings.query.first()
    s.hostname = request.form.get('hostname')
    s.password = request.form.get('password')
    s.interval = int(0 if request.form.get('interval') == '' else request.form.get('interval')) # TODO modify duet_status job with new interval
    s.brightness = float(request.form.get('brightness'))
    pixels.brightness = s.brightness
    s.invert_dir = 1 if request.form.get('invert-dir') == 'true' else 0

    s.order = request.form.get('order')
    if s.order == 'RGB':
        app.config['ORDER'] = neopixel.RGB
    elif s.order == 'RGBW':
        app.config['ORDER'] = neopixel.RGBW
    elif s.order == 'GRB':
        app.config['ORDER'] = neopixel.GRB
    elif s.order == 'GRBW':
        app.config['ORDER'] = neopixel.GRBW
    pixels.order = app.config['ORDER']
    
    s.pixel_pin = int(0 if request.form.get('neo1pin', '') == '' else request.form.get('neo1pin'))
    if s.pixel_pin == 10:
        app.config['PIXEL_PIN'] = board.D10
    elif s.pixel_pin == 12:
        app.config['PIXEL_PIN'] = board.D12
    elif s.pixel_pin == 18:
        app.config['PIXEL_PIN'] = board.D18
    elif s.pixel_pin == 21:
        app.config['PIXEL_PIN'] = board.D21
    #pixels.pin = app.config['PIXEL_PIN'] # TODO - figure out way to change after instantiated -- currently gives error

    db.session.add(s)
    db.session.commit()

    logger.info('<-update_settings-> Settings updated.')
    return jsonify({'msg': 'Settings saved.'})

@app.route('/get_status', methods=['GET', 'POST'])
def get_status():
    logger.debug('<-get_status-> Returning current printer status:{}.'.format(printer.get_status()))
    return jsonify(printer.get_status())

###########################
#### ledcontrol routes ####
###########################

@app.route('/')
@app.route('/index')
@app.route('/ledcontrol')
def ledcontrol():
    # TODO: Fix this ugly hack for converting param db query to usable dict object
    params = Param.query.all()
    rings = {}
    for p in params:
        rings[p.ringnum] = {}
    for p in params:
        rings[p.ringnum][p.event] = p.get_obj()

    return render_template('led.html', rings=rings)

@app.route('/get_action_params', methods=['GET', 'POST'])
def get_action_params():
    params = Param.query.filter_by(ringnum=int(request.form.get('ring')), event=request.form.get('event')).first().get_obj()
    return jsonify({'params': params})

@app.route('/update_action', methods=['GET', 'POST'])
def update_action():
    params = Param.query.filter_by(ringnum=int(request.form.get('ring')), event=request.form.get('event')).first()
    params.action = int(request.form.get('action'))
    params.color1 = request.form.get('color1', 'rgb(0, 0, 0)')
    params.color2 = request.form.get('color2','rgb(0, 0, 0)')
    params.interval = float(request.form.get('interval'))
    db.session.add(params)
    db.session.commit()
    logger.info('<-update_action-> Param updated.')
    printer.needs_update = True
    return jsonify({'msg': 'Action saved.'})

@app.route('/test_event', methods=['GET', 'POST'])
def test_event():
    settings = Settings.query.first()
    ring_num = int(request.form.get('ring'))
    action_params = {
        'action': int(request.form.get('action')),
        'color1': request.form.get('color1'),
        'color2': request.form.get('color2'),
        'interval': float(request.form.get('interval'))
    }
    at = ActionThread(action_params, printer, pixels, ring_num)
    at.setName('test{}'.format(ring_num))
    at.daemon = True
    at.start()
    logger.info('<-test_event-> Test Started.')
    return jsonify({'msg': 'Test Started!'})


###########################
####    debug routes   ####
###########################

@app.route('/debug')
def debug_page():
    data = json.load(open('mockDuet/data.json'))
    return render_template('debug.html', data=data)

@app.route('/debug/get_log', methods=['POST'])
def get_log():
    f = open(app.config['LOGFILE'], 'r')
    log = f.read()
    return jsonify({'log': log})

@app.route('/debug/status', methods=['POST'])
def debug_status():
    s = Settings.query.first()
    host = 'http://' + s.hostname + '/rr_status'
    args = {'type': request.form.get('type')}
    response = None
    try:
        response = requests.get(host, params=args)
    except:
        logger.debug('<-debug_status-> ***ERROR*** trying to get status host:{} args:{} response:{}'.format(host, args, sys.exc_info()[0]))
    if response is not None and response.status_code == 200:
        logger.debug('<-debug_status-> Printer status received.')
        return jsonify({'status': str(response.json())})
    else:
        logger.debug('<-debug_status-> No response received')
        return jsonify({'status': 'Error: No response received.'})

@app.route('/debug/set_printer', methods=['POST'])
def debug_setprinter():
    data = json.load(open('mockDuet/data.json'))
    data['status'] = request.form.get('printer-status')
    data['temps']['tools']['active'][0][0] = 100 # set hotened target to 100 to normalize percent
    data['temps']['current'][1] = float(request.form.get('hotend-percent'))
    data['temps']['bed']['active'] = 100 # set heatbed target to 100 to normalize percent
    data['temps']['current'][0] = float(request.form.get('heatbed-percent'))
    data['fractionPrinted'] = float(request.form.get('print-percent'))

    with open('mockDuet/data.json', 'w') as outfile:
        json.dump(data, outfile)

    return jsonify({'result': 'OK'})

@app.route('/debug/sim_mode', methods=['POST'])
def debug_simmode():
    mode = request.form.get('mode')
    app.config['SIM_MODE'] = True if mode == 'true' else False

    return jsonify({'result': mode})

@app.route('/debug/set_loglevel', methods=['POST'])
def debug_set_loglevel():
    level = request.form.get('loglevel', 'debug').lower()
    if level == 'info':
        logger.setLevel(logging.INFO)
    elif level == 'debug':
        logger.setLevel(logging.DEBUG)
    s = Settings.query.first()
    s.loglevel = level
    db.session.add(s)
    db.session.commit()

    return jsonify({'result': level})

@app.route('/debug/reset_to_defaults')
def reset_to_defaults():
    logger.info('<-reset_to_defaults-> Dropping all db tables...')
    db.drop_all()
    logger.info('<-reset_to_defaults-> Creating all db tables...')
    db.create_all()
    
    logger.info('<-reset_to_defaults-> Adding default Settings values...')
    defaults = json.load(open('app/settings.default.json'))
    s = Settings(
        hostname = defaults['hostname'],
        password = defaults['password'],
        pixel_pin = defaults['pixel_pin'],
        interval = defaults['interval'],
        order = defaults['order'],
        num_pixels = defaults['num_pixels'],
        num_rings = defaults['num_rings']
    )
    db.session.add(s)
    db.session.commit()
    logger.info('<-reset_to_defaults-> Settings Done!')

    logger.info('<-reset_to_defaults-> Adding default Param values...')
    defaults = json.load(open('app/params.default.json'))
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
    logger.info('<-reset_to_defaults-> Done! Redirecting to /')
    return redirect('/')