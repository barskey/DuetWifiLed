import requests
from flask import current_app
from project.models import db, Settings, Param
from project import scheduler
from project.printer_status import PrinterStatus
import time
#import board
#import neopixel

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
        # TODO: Fix this ungly hack for converting param db query to usable dict object
        rings = {}
        for p in params:
            rings[p.ringnum] = {}
        for p in params:
            rings[p.ringnum][p.event] = p.get_obj()

        for ringnum,events in rings.items():
            params = events[printer.get_event()] #  get params for action to take for this printer state
            print ('Ring {}: Do action {}!'.format(ringnum, params['action']))

def solid_color(color, order, ringnum):
    # color passed in as 'rgb(#, #, #)'
    c = tuple(x.strip() for x in color1[4:-1].split(','))
    for i in [0:15]:
        pixnum = i + 16 * (ringnum - 1)
        if order == "RGB":
            #pixels[pixnum] = c
            pass
        else:
            #pixels[pixnum] = (c[1],c[0],c[2])
            pass
    #pixels.show()

def temp(percent, color, background, ringnum):
    # color passed in as 'rgb(#, #, #)'
    # percent passed in as % complete
    c = tuple(x.strip() for x in color[4:-1].split(','))
    b = tuple(x.strip() for x in background[4:-1].split(','))

    for i in [0:15]:
        pixnum = i + 16 * (ringnum - 1)
        if order == "RGB":
            #pixels[pixnum] = c if percent >= (i + 1)/16 else b
            pass
        else:
            #pixels[pixnum] = (c[1],c[0],c[2]) if percent >= (i + 1)/16 else (b[1], b[0], b[2])
            pass
    #pixels.show()

def flash(color1, color2, ringnum, interval):
    # colors passed in as 'rgb(#, #, #)'
    c1 = tuple(x.strip() for x in color1[4:-1].split(','))
    c2 = tuple(x.strip() for x in color2[4:-1].split(','))

    while True:
        for i in range(16):
            pixnum = i + 16 * (ringnum - 1)
            if order == "RGB":
                #pixels[pixnum] = c1
                pass
            else:
                #pixels[pixnum] = (c1[1],c1[0],c1[2])
                pass
        #pixels.show()
        # swap colors
        c1, c2 = c2, c1
        time.sleep(interval)

def breathe(color1, color2, ringnum, interval):
    # colors passed in as 'rgb(#, #, #)'
    c1 = tuple(x.strip() for x in color1[4:-1].split(','))
    c2 = tuple(x.strip() for x in color2[4:-1].split(','))

    while True:
        counter = 1
        for t in range(0, 1, .01): # use 0.01 increment for color change (100 steps)
            color = tuple(round(x + (y - x) * t) for x,y in zip(c1, c2)) # lerp between each color channel over increment
            #rt = r1 + (r2 - r1) * t
            #gt = g1 + (g2 - g1) * t
            #bt = b1 + (b2 - b1) * t
            for i in range(16): # set all pixels in this ring to current color
                pixnum = i + 16 * (ringnum - 1)
                if order == "RGB":
                    #pixels[pixnum] = color
                    pass
                else:
                    #pixels[pixnum] = (color[1],color[0],color[2])
                    pass
            #pixels.show()
            t = sleep_time(counter, interval)
            print ('sleep:{} color:{}'.format(t, color)) # debug
            time.sleep(t)
            counter = counter + 1
        # swap colors for next loop so it goes back and forth
        c1, c2 = c2, c1

def chase(color, background, ringnum, interval):
    # color passed in as 'rgb(#, #, #)'
    c = tuple(x.strip() for x in color[4:-1].split(','))
    b = tuple(x.strip() for x in background[4:-1].split(','))

    pos = 1 # highlited pixel position in ring (from 1 to 16)
    while True:
        for i in [0:15]:
            pixnum = i + 16 * (ringnum - 1)
            if order == "RGB":
                #pixels[pixnum] = c if i == pos - 1 else b
                pass
            else:
                #pixels[pixnum] = (c[1], c[0], c[2]) if i == pos - 1 else (b[1], b[0], b[2])
                pass
        #pixels.show()
        t = sleep_time(pos, interval, 16)
        print ('pos:{} sleep:{}'.format(pos, t)) # debug
        pos = pos + 1 if pos < 16 else 0
        time.sleep(t)

def sleep_time(num, duration, num_steps=100):
    # uses quadratic ease in/out to return time to wait/sleep
    # num is this step number (should go from 0 to num_steps)
    # duration is total time that will be used
    # num_steps is number of steps to use over entire duration -- defaults to 100
    increment = duration / num_steps
    this_step = ease(increment * num)
    last_step = ease(increment * (num - 1))

    return this_step - last_step # returns delta change from last step, which is how long to wait this step

def ease(t):
    # returns quadratic ease in/out of given t -- expected in range bet 0 and 1
    if t <= 0.5: # use for ease-in half of curve
        return 2 * t ** 2
    t = t - 0.5
    return 2 * t * (1 - t) + 0.5 # use for ease-out half of curve
