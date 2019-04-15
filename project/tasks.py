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
    rgb = color[4:-1].split(',')
    r = rgb[0].strip()
    g = rgb[1].strip()
    b = rgb[2].strip()
    for i in [0:15]:
        pixnum = i + 16 * (ringnum - 1)
        if order == "RGB":
            #pixels[pixnum] = (r,g,b)
            pass
        else:
            #pixels[pixnum] = (g,r,b)
            pass
    #pixels.show()

def temp(percent, color, background, ringnum):
    # color passed in as 'rgb(#, #, #)'
    # percent passed in as % complete
    rgb = color[4:-1].split(',')
    c_r = rgb[0].strip()
    c_g = rgb[1].strip()
    c_b = rgb[2].strip()

    rgb = background[4:-1].split(',')
    b_r = rgb[0].strip()
    b_g = rgb[1].strip()
    b_b = rgb[2].strip()

    for i in [0:15]:
        pixnum = i + 16 * (ringnum - 1)
        if order == "RGB":
            #pixels[pixnum] = (c_r,c_g,c_b) if percent >= (i + 1)/16 else (b_r, b_g, b_b)
            pass
        else:
            #pixels[pixnum] = (c_g,c_r,c_b) if percent >= (i + 1)/16 else (b_g, b_r, b_b)
            pass
    #pixels.show()

def flash(color1, color2, ringnum, interval):
    # colors passed in as 'rgb(#, #, #)'
    rgb = color1[4:-1].split(',')
    r1 = rgb[0].strip()
    g1 = rgb[1].strip()
    b1 = rgb[2].strip()

    rgb = color2[4:-1].split(',')
    r2 = rgb[0].strip()
    g2 = rgb[1].strip()
    b2 = rgb[2].strip()

    tick = True
    while True:
        for i in range(16):
            pixnum = i + 16 * (ringnum - 1)
            if order == "RGB":
                #pixels[pixnum] = (r1,g1,b1) if tick else (r2,g2,b2)
                pass
            else:
                #pixels[pixnum] = (g1,r1,b1) if tick else (g2,r2,b2)
                pass
        #pixels.show()
        tick = not tick
        time.sleep(interval)

def breathe(color1, color2, ringnum, interval):
    # colors passed in as 'rgb(#, #, #)'
    rgb = color1[4:-1].split(',')
    r1 = rgb[0].strip()
    g1 = rgb[1].strip()
    b1 = rgb[2].strip()

    rgb = color2[4:-1].split(',')
    r2 = rgb[0].strip()
    g2 = rgb[1].strip()
    b2 = rgb[2].strip()

    for t in range(0, 1, .01):
        rt = (r2 - r1) * t
        for i in range(16):
            pixnum = i + 16 * (ringnum - 1)
            if order == "RGB":
                #pixels[pixnum] = (r1,g1,b1) if tick else (r2,g2,b2)
                pass
            else:
                #pixels[pixnum] = (g1,r1,b1) if tick else (g2,r2,b2)
                pass
        #pixels.show()
        tick = not tick
        time.sleep(interval)