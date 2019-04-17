import requests
import time
import threading
from project.models import db, Settings, Param
from project import scheduler
from project.printer_status import PrinterStatus
from easing_functions import CubicEaseInOut
#import board
#import neopixel
from flask import current_app

printer = PrinterStatus()
#pixels = neopixel.NeoPixel(board.D18, 48)

# communication task for duet status
@scheduler.task('interval', id='duet_status', seconds=5)
def get_status():
    response = None
    with scheduler.app.app_context():
        s = Settings.query.first()
        host = 'http://' + s.hostname + '/rr_status'
        #print(host)
        host = 'http://localhost:5001/rr_status'
        args = {'type': '2'}
        response = requests.post(host, json=args)
    if response.status_code == requests.codes.ok:
        printer.update_status(response.json())
        update_rings()
    #return result.json()

def update_rings():
    with scheduler.app.app_context():
        params = Param.query.all()
        # put results in organized dict object
        # TODO: Fix this double for-loop hack for converting param db query to usable dict object
        rings = {}
        for p in params:
            rings[p.ringnum] = {}
        for p in params:
            rings[p.ringnum][p.event] = p.get_obj()

        for ring_num,events in rings.items():
            action_params = events[printer.get_event()] #  get params for action to take for current printer state
            run_action(ring_num, action_params)
            #print ('Ring {}: Do action {}!'.format(ring_num, action_num))

def run_action(ring_num, params):
    action_num = params['action']
    c1 = params['color1']
    c2 = params['color2']
    interval = params['interval']
    order = 'RGB' # TODO get setting from db for order
    if action_num == 2:       # solid
        solid_color(c1, order, ring_num)
    elif action_num == 3:     # hotened temp
        temp('h', c1, c2, order, ring_num)
    elif action_num == 4:     # heatbed temp
        temp('b', c1, c2, order, ring_num)
    elif action_num == 5:     # flash
        flash(c1, c2, order, ring_num, interval, True)
    elif action_num == 6:     # breathe
        breathe(c1, c2, order, ring_num, interval, True)
    elif action_num == 7:     # chase
        chase(c1, c2, order, ring_num, interval, True)


def solid_color(color, order, ringnum):
    # color: like 'rgb(#, #, #)'
    c = tuple(int(x.strip()) for x in color[4:-1].split(','))
    for i in range(16):
        pixnum = i + 16 * (ringnum - 1)
        if order == 'RGB':
            #pixels[pixnum] = c
            pass
        else:
            #pixels[pixnum] = (c[1],c[0],c[2])
            pass
    #pixels.show()
    with current_app.app_context():
        current_app.logger.info('Ring {} is now color {}'.format(ringnum, c))

def temp(source, color, background, order, ringnum):
    # color: like 'rgb(#, #, #)'
    # source: 'h' for hotend 'b' for heatbed
    c = tuple(int(x.strip()) for x in color[4:-1].split(','))
    b = tuple(int(x.strip()) for x in background[4:-1].split(','))

    percent = printer.heatbedTemp if source == 'b' else printer.hotendTemp
    debug1, debug2 = '', ''
    for i in range(16):
        pixnum = i + 16 * (ringnum - 1)
        if order == 'RGB':
            #pixels[pixnum] = c if percent >= i/16 else b
            if percent >= i/16:
                debug1 = debug1 + str(i)
            else:
                debug2 = debug2 + str(i)
        else:
            #pixels[pixnum] = (c[1],c[0],c[2]) if percent >= i/16 else (b[1], b[0], b[2])
            pass
    #pixels.show()
    print ('Ring {} temp pixels {} are color {}. Background pixels {} are color {}'.format(ringnum, debug1, c, debug2, b))

def flash(color1, color2, order, ringnum, interval, test=False):
    # color1,2: like 'rgb(#, #, #)'
    c1 = tuple(int(x.strip()) for x in color1[4:-1].split(','))
    c2 = tuple(int(x.strip()) for x in color2[4:-1].split(','))

    loop_counter = 2 # use to run a certain number of loops in when called with test True
    while True:
        if test is True and loop_counter <= 0:
            break
        for i in range(16):
            pixnum = i + 16 * (ringnum - 1)
            if order == 'RGB':
                #pixels[pixnum] = c1
                pass
            else:
                #pixels[pixnum] = (c1[1],c1[0],c1[2])
                pass
        #pixels.show()
        # swap colors
        c1, c2 = c2, c1
        time.sleep(interval)
        loop_counter = loop_counter - 1
        print ('Ring {} is now color {}'.format(ringnum, c1))

def breathe(color1, color2, order, ringnum, interval, test=False):
    # colors passed in as 'rgb(#, #, #)'
    c1 = tuple(int(x.strip()) for x in color1[4:-1].split(','))
    c2 = tuple(int(x.strip()) for x in color2[4:-1].split(','))

    num_steps = 100 # convenience for changing number of steps for color change
    # create easing instance for smoothing animations
    e = CubicEaseInOut(0, interval, num_steps) # will go from 0 to interval in num_steps steps
    loop_counter = 2 # use to run a certain number of loops in when called with test True
    while True:
        if test is True and loop_counter <= 0:
            break
        last_sleep = 0
        for n in range(num_steps): # use 0.01 increment for color change (100 steps)
            t = n / num_steps if n > 0 else 0
            color = tuple(round(x + (y - x) * t) for x,y in zip(c1, c2)) # lerp between each color channel over increment
            #rt = r1 + (r2 - r1) * t
            #gt = g1 + (g2 - g1) * t
            #bt = b1 + (b2 - b1) * t
            for i in range(16): # set all pixels in this ring to current color
                pixnum = i + 16 * (ringnum - 1)
                if order == 'RGB':
                    #pixels[pixnum] = color
                    pass
                else:
                    #pixels[pixnum] = (color[1],color[0],color[2])
                    pass
            #pixels.show()
            s = e.ease(n) - last_sleep # gets the sleep time using cubic ease-in/out
            last_sleep = e.ease(n) # save this sleep time for subtracting from next round
            #print ('step:{} color:{}'.format(n, color)) # debug
            time.sleep(s)
        # swap colors for next loop so it goes back and forth
        print ('Breathe: Ring {} is now color {}'.format(ringnum, c1))
        c1, c2 = c2, c1
        loop_counter = loop_counter - 1

def chase(color, background, order, ringnum, interval, test=False):
    # color passed in as 'rgb(#, #, #)'
    c = tuple(int(x.strip()) for x in color[4:-1].split(','))
    b = tuple(int(x.strip()) for x in background[4:-1].split(','))

    # creates easing instance for smoothing animations
    e = CubicEaseInOut(0, interval, 16) # will go from 0 to interval in 16 steps
    loop_counter = 2 # use to run a certain number of loops in when called with test True
    while True:
        if test is True and loop_counter <= 0:
            break
        last_sleep = 0
        for pos in range(16):
            for i in range(16): # step through all pixels in this ring
                pixnum = i + 16 * (ringnum - 1)
                if order == 'RGB':
                    #pixels[pixnum] = c if i == pos else b
                    pass
                else:
                    #pixels[pixnum] = (c[1], c[0], c[2]) if i == pos else (b[1], b[0], b[2])
                    pass
            #pixels.show()
            s = e.ease(pos) - last_sleep # gets the sleep time using cubic ease-in/out
            last_sleep = e.ease(pos) # save this sleep time for subtracting from next round
            #print ('pos:{} sleep:{}'.format(pos, s)) # debug
            time.sleep(s)
        print ('Chase: Ring {} loop completed - chase color {}'.format(ringnum, c1))
        loop_counter = loop_counter - 1
