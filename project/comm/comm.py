import requests
from . import comm_blueprint
from project.models import db, Settings


def get_status(type):
    s = Settings.query.first()
    host = 'http://' + s.hostname + '/rr_status'
    args = {'type': type}
    print(host)
    result = requests.post(host, json=args)
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