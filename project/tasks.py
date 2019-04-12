import requests
from flask import current_app
from project.models import db, Settings, Param
from project import scheduler
from project.printer_status import PrinterStatus

printer = PrinterStatus()

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