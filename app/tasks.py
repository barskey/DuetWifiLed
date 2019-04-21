import requests
import time
from threading import Thread
from app import db, logger, scheduler, printer
from app.models import Settings, Param
from easing_functions import CubicEaseInOut
from flask import current_app
#import board
#import neopixel

#pixels = neopixel.NeoPixel(board.D18, 48)

def update_rings():
    with current_app.app_context():
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
    if action_num in [0,1,2]:
        return

    c1 = params['color1']
    c2 = params['color2']
    interval = params['interval']
    order = 'RGB' # TODO get setting from db for order

    t = None
    if action_num == 2:       # solid
        t = Thread(target=solid_color, args=(c1, order, ring_num))
    elif action_num == 3:     # hotend temp
        t = Thread(target=temp, args=('h', c1, c2, order, ring_num), name='ring{}'.format(ring_num))
    elif action_num == 4:     # heatbed temp
        t = Thread(target=temp, args=('b', c1, c2, order, ring_num), name='ring{}'.format(ring_num))
    elif action_num == 5:     # flash
        t = Thread(target=flash, args=(c1, c2, order, ring_num, interval), name='ring{}'.format(ring_num))
    elif action_num == 6:     # breathe
        t = Thread(target=breathe, args=(c1, c2, order, ring_num, interval), name='ring{}'.format(ring_num))
    elif action_num == 7:     # chase
        t = Thread(target=chase, args=(c1, c2, order, ring_num, interval), name='ring{}'.format(ring_num))
    t.daemon = True
    t.start()
    printer.set_task(ring_num, t)


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
    logger.info('::solid::   Ring:{} color:{}'.format(ringnum, c))

def temp(source, color, background, order, ringnum, test=False):
    # color: like 'rgb(#, #, #)'
    # source: 'h' for hotend 'b' for heatbed
    c = tuple(int(x.strip()) for x in color[4:-1].split(','))
    b = tuple(int(x.strip()) for x in background[4:-1].split(','))

    loop_counter = 2 # use to run a certain number of loops in when called with test True
    while True:
        if test is True and loop_counter <= 0:
            break
        percent = printer.heatbedTemp if source == 'b' else printer.hotendTemp
        print('temp:{}'.format(printer.hotendTemp))
        for i in range(16):
            pixnum = i + 16 * (ringnum - 1)
            if order == 'RGB':
                #pixels[pixnum] = c if percent >= i/16 else b
                pass
            else:
                #pixels[pixnum] = (c[1],c[0],c[2]) if percent >= i/16 else (b[1], b[0], b[2])
                pass
        #pixels.show()
        logger.info('::temp::    Ring:{} color:{} background:{}'.format(ringnum, c, b))
        loop_counter = loop_counter - 1
        time.sleep(1) # update temp every 1 second

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
        logger.info('::flash::   Ring:{} color:{}'.format(ringnum, c1))

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
        logger.info('::breathe:: Ring:{} color:{}'.format(ringnum, c1))
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
        logger.info('::chase::   Ring:{} loop completed - chase color:{}'.format(ringnum, c))
        loop_counter = loop_counter - 1
