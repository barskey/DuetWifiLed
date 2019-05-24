import threading
import time
from app import app, logger
from easing_functions import CubicEaseInOut
import neopixel

class ActionThread(threading.Thread):
    """Thread class that will stop itself when joined."""

    def __init__(self, params, printer, pixels, ring, *args, **kwargs):
        super(ActionThread, self).__init__(*args, **kwargs)
        self._action_num = params['action']
        self._ringnum = int(ring)
        self._color1 = params['color1']
        self._color2 = params['color2']
        self._interval = params['interval']

        self.n = app.config['NEO_PIXELS'] # for convenience
        self.order = app.config['ORDER'] # for convenience
        self.inv_dir = app.config['INV_DIR'] # for convenience

        self._pixels = pixels
        self._printer = printer
        self._stopevent = threading.Event()

    def stopped(self):
        return self._stopevent.is_set()

    def join(self, timeout=None):
        """ Stop the thread. """
        logger.debug('<-ActionThread-> Stopping thread {}...'.format(self.getName()))
        self._stopevent.set()
        self.clean_up()
        threading.Thread.join(self, timeout)

    def run(self):
        if self._action_num in [0,1]:
            logger.debug('<-ActionThread-> {} set to no change.'.format(self.getName()))
        elif self._action_num == 2:
            logger.debug('<-ActionThread-> {} running solid.'.format(self.getName()))
            self.solid_color()
        elif self._action_num == 3:
            logger.debug('<-ActionThread-> {} running hotend temp.'.format(self.getName()))
            self.temp('h')
        elif self._action_num == 4:
            logger.debug('<-ActionThread-> {} running heatbed temp.'.format(self.getName()))
            self.temp('b')
        elif self._action_num == 5:
            logger.debug('<-ActionThread-> {} running print percent.'.format(self.getName()))
            self.print_percent()
        elif self._action_num == 6:
            logger.debug('<-ActionThread-> {} running flash.'.format(self.getName()))
            self.flash()
        elif self._action_num == 7:
            logger.debug('<-ActionThread-> {} running breathe.'.format(self.getName()))
            self.breathe()
        elif self._action_num == 8:
            logger.debug('<-ActionThread-> {} running chase.'.format(self.getName()))
            self.chase()
        elif self._action_num == 9:
            logger.debug('<-ActionThread-> {} running rainbow.'.format(self.getName()))
            self.rainbow()

    def solid_color(self):
        # self._color: like 'rgb(#, #, #)'
        c = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        if self.order == neopixel.RGBW or self.order == neopixel.GRBW:
            c = c + (0,)
        for i in range(self.n):
            pixnum = i + self.n * (self._ringnum - 1)
            self._pixels[pixnum] = c
        self._pixels.show()
        logger.debug('<-solid->   Ring:{} color:{}'.format(self._ringnum, c))

    def temp(self, source, test=False):
        # self._color: like 'rgb(#, #, #)'
        # source: 'h' for hotend 'b' for heatbed
        c = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        b = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))
        if self.order == neopixel.RGBW or self.order == neopixel.GRBW:
            c = c + (0,)
            b = b + (0,)

        loop_counter = 2 # use to run a certain number of loops when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            percent = self._printer.heatbedTemp if source == 'b' else self._printer.hotendTemp
            for i in reversed(range(self.n)) if self.inv_dir == 1 else range(self.n): # repeat 16 times - once for each pixel in ring
                pixnum = i + self.n * (self._ringnum - 1) # adjust pixnum for ring number
                pix_percent = (percent - i/self.n)/(1/self.n) # normalize percentage complete to this pixel range
                if pix_percent < 0: # background pixel
                    self._pixels[pixnum] = b
                    pass
                elif pix_percent >= 1: # full percent pixel
                    self._pixels[pixnum] = c
                    pass
                else: # fade color from off (0) to full color
                    cx = tuple(round(x * pix_percent) for x in c)
                    self._pixels[pixnum] = cx
            self._pixels.show()
            logger.debug('<-temp->    Ring:{} %:{} color:{} background:{}'.format(self._ringnum, percent, c, b))
            loop_counter = loop_counter - 1
            time.sleep(1) # update temp every 1 second

    def print_percent(self, test=False):
        # self._color: like 'rgb(#, #, #)'
        c = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        b = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))
        if self.order == neopixel.RGBW or self.order == neopixel.GRBW:
            c = c + (0,)
            b = b + (0,)

        loop_counter = 2 # use to run a certain number of loops when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            percent = self._printer.percentComplete / 100 # need percent as decimal bet 0 and 1
            for i in reversed(range(self.n)) if self.inv_dir == 1 else range(self.n): # repeat 16 times - once for each pixel in ring
                pixnum = i + self.n * (self._ringnum - 1) # adjust pixnum for ring number
                pix_percent = (percent - i/self.n)/(1/self.n) # normalize percentage complete to this pixel range
                if pix_percent < 0: # background pixel
                    self._pixels[pixnum] = b
                    pass
                elif pix_percent >= 1: # full percent pixel
                    self._pixels[pixnum] = c
                    pass
                else: # fade color from off (0) to full color
                    cx = tuple(round(x * pix_percent) for x in c)
                    self._pixels[pixnum] = cx
            self._pixels.show()
            logger.debug('<-print_%-> Ring:{} %:{} color:{} background:{}'.format(self._ringnum, percent, c, b))
            loop_counter = loop_counter - 1
            time.sleep(1) # update temp every 1 second

    def flash(self, test=False):
        # self._color: like 'rgb(#, #, #)'
        c1 = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        c2 = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))
        if self.order == neopixel.RGBW or self.order == neopixel.GRBW:
            c1 = c1 + (0,)
            c2 = c2 + (0,)

        loop_counter = 2 # use to run a certain number of loops when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            for i in range(self.n):
                pixnum = i + self.n * (self._ringnum - 1)
                self._pixels[pixnum] = c1
            self._pixels.show()
            # swap colors
            c1, c2 = c2, c1
            time.sleep(self._interval)
            loop_counter = loop_counter - 1
            logger.debug('<-flash->   Ring:{} color:{}'.format(self._ringnum, c1))

    def breathe(self, test=False):
        # self._color: like 'rgb(#, #, #)'
        c1 = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        c2 = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))
        if self.order == neopixel.RGBW or self.order == neopixel.GRBW:
            c1 = c1 + (0,)
            c2 = c2 + (0,)

        num_steps = 100 # convenience for changing number of steps for color change
        # create easing instance for smoothing animations
        e = CubicEaseInOut(0, self._interval, num_steps) # will go from 0 to interval in num_steps steps
        loop_counter = 2 # use to run a certain number of loops when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            last_sleep = 0
            for n in range(num_steps): # use 0.01 increment for color change (100 steps)
                t = n / num_steps if n > 0 else 0
                color = tuple(round(x + (y - x) * t) for x,y in zip(c1, c2)) # lerp between each color channel over increment
                for i in range(self.n): # set all pixels in this ring to current color
                    pixnum = i + self.n * (self._ringnum - 1)
                    self._pixels[pixnum] = color
                self._pixels.show()
                s = e.ease(n) - last_sleep # gets the sleep time using cubic ease-in/out
                last_sleep = e.ease(n) # save this sleep time for subtracting from next round
                #print ('step:{} color:{}'.format(n, color)) # debug
                time.sleep(s)
            # swap colors for next loop so it goes back and forth
            logger.debug('<-breathe-> Ring:{} color:{}'.format(self._ringnum, c1))
            c1, c2 = c2, c1
            loop_counter = loop_counter - 1

    def chase(self, test=False):
        # self._color: like 'rgb(#, #, #)'
        c = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        b = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))
        if self.order == neopixel.RGBW or self.order == neopixel.GRBW:
            c = c + (0,)
            b = b + (0,)

        # creates easing instance for smoothing animations
        e = CubicEaseInOut(0, self._interval, self.n) # will go from 0 to interval in 16 steps
        loop_counter = 2 # use to run a certain number of loops when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            last_sleep = 0
            for pos in reversed(range(self.n)) if self.inv_dir == 1 else range(self.n):
                for i in reversed(range(self.n)) if self.inv_dir == 1 else range(self.n): # step through all pixels in this ring
                    pixnum = i + self.n * (self._ringnum - 1)
                    self._pixels[pixnum] = c if i == pos else b
                self._pixels.show()
                p = self.n - (pos - 1) if self.inv_dir == 1 else pos
                s = e.ease(p) - last_sleep # gets the sleep time using cubic ease-in/out
                last_sleep = e.ease(p) # save this sleep time for subtracting from next round
                #print ('pos:{} sleep:{}'.format(pos, s)) # debug
                time.sleep(s)
            logger.debug('<-chase->   Ring:{} loop completed - chase color:{}'.format(self._ringnum, c))
            loop_counter = loop_counter - 1

    def rainbow(self, test=False):
        loop_counter = 2 # use to run a certain number of loops when called with test True
        wait = self._interval / 255 # one rainbow cycle is 255 colors
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            for j in range(255):
                for i in reversed(range(self.n)) if self.inv_dir == 1 else range(self.n):
                    pixnum = i + self.n * (self._ringnum - 1)
                    pixel_index = (i * 256 // self.n) + j # // is floor division
                    self._pixels[pixnum] = self.wheel(pixel_index & 255) # bitwise and makes sure it is always less than 255
                self._pixels.show()
                time.sleep(wait)
            logger.debug('<-rainbow-> Ring:{} loop completed'.format(self._ringnum))
            loop_counter = loop_counter - 1

    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos*3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos*3)
            g = 0
            b = int(pos*3)
        else:
            pos -= 170
            r = 0
            g = int(pos*3)
            b = int(255 - pos*3)
        return (r, g, b) if self.order == neopixel.RGB or self.order == neopixel.GRB else (r, g, b, 0)

    def clean_up(self):
        for i in range(self.n): # repeat 16 times - once for each pixel in ring
            pixnum = i + self.n * (self._ringnum - 1) # adjust pixnum for ring number
            self._pixels[pixnum] = (0, 0, 0) if self.order == neopixel.RGB or self.order == neopixel.GRB else (0, 0, 0, 0)
        self._pixels.show()