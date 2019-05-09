from app import app, db, logger, printer, pixels, ORDER, PIXEL_PIN
from flask import render_template, redirect, url_for, request, jsonify
import json
from app.models import Settings, Param
from app.actions import ActionThread

###########################
####    setup routes   ####
###########################

@app.route('/settings')
def settings():
    # if Settings can't be queried, reset to defaults to create tables and load defaults
    try:
        Settings.query.all()
    except:
        return redirect('/reset_to_defaults')

    settings = Settings.query.first()
    return render_template('settings.html', settings=settings)

@app.route('/update_settings', methods=['GET', 'POST'])
def update_settings():
    s = Settings.query.first()
    s.hostname = request.form.get('hostname')
    s.password = request.form.get('password')
    s.interval = int(0 if request.form.get('interval') == '' else request.form.get('interval'))
    s.neo1pin = int(0 if request.form.get('neo1pin') == '' else request.form.get('neo1pin'))
    s.neo2pin = int(0 if request.form.get('neo2pin') == '' else request.form.get('neo2pin'))
    s.neo3pin = int(0 if request.form.get('neo3pin') == '' else request.form.get('neo3pin'))
    s.order = request.form.get('order')
    if s.order == 'RGB':
        ORDER = neopixel.RGB
    elif s.order == 'RGBW':
        ORDER = neopixel.RGBW
    elif s.order == 'GRB':
        ORDER = neopixel.GRB
    elif s.order == 'GRBW':
        ORDER = neoixel.GRBW
    pixels.pixel_order = ORDER
    
    if s.neopin == 10:
        PIXEL_PIN = board.D10
    elif s.neopin == 12:
        PIXEL_PIN = board.D12
    elif s.neopin == 18:
        PIXEL_PIN = board.D18
    elif s.neopin == 21:
        PIXEL_PIN = board.D21
    pixels.pixel_pin = PIXEL_PIN

    db.session.add(s)
    db.session.commit()

    logger.info('<-update_settings-> Settings updated.')
    return jsonify({'msg': 'Settings saved.'})

@app.route('/get_status', methods=['GET', 'POST'])
def update_status():
    logger.debug('<-get_status-> Returning current printer status:{}.'.format(printer.get_status()))
    return jsonify(printer.get_status())

@app.route('/reset_to_defaults')
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
        neo1pin = defaults['neo1pin'],
        neo2pin = defaults['neo2pin'],
        neo3pin = defaults['neo3pin'],
        interval = defaults['interval'],
        order = defaults['order']
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

###########################
#### ledcontrol routes ####
###########################

@app.route('/')
@app.route('/index')
@app.route('/ledcontrol')
def ledcontrol():
    # if Settings can't be queried, reset to defaults to create tables and load defaults
    try:
        Settings.query.all()
    except:
        return redirect('/reset_to_defaults')

    # if Param can't be queried, reset to defaults to create tables and load defaults
    try:
        Param.query.all()
    except:
        return redirect('/reset_to_defaults')

    # TODO: Fix this ugly hack for converting param db query to usable dict object
    params = Param.query.all()
    rings = {}
    for p in params:
        rings[p.ringnum] = {}
    for p in params:
        rings[p.ringnum][p.event] = p.get_obj()
    #print(rings)

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
    order = settings.order
    ring_num = int(request.form.get('ring'))
    action_params = {
        'action': int(request.form.get('action')),
        'color1': request.form.get('color1'),
        'color2': request.form.get('color2'),
        'interval': float(request.form.get('interval'))
    }
    at = ActionThread(action_params, printer, ring_num, order)
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
    # if Settings can't be queried, reset to defaults to create tables and load defaults
    try:
        Settings.query.all()
    except:
        return redirect('/reset_to_defaults')

    # if Param can't be queried, reset to defaults to create tables and load defaults
    try:
        Param.query.all()
    except:
        return redirect('/reset_to_defaults')

    settings = Settings.query.first()
    return render_template('debug.html', settings=settings)
