import threading
import time
from app import logger
from easing_functions import CubicEaseInOut

class ActionThread(threading.Thread):
    """Thread class that will stop itself when joined."""

    def __init__(self, params, printer, ring, order='RGB', *args, **kwargs):
        super(ActionThread, self).__init__(*args, **kwargs)
        self._action_num = params['action']
        self._ringnum = ring
        self._color1 = params['color1']
        self._color2 = params['color2']
        self._interval = params['interval']
        self._order = order

        self._printer = printer
        self._stopevent = threading.Event()

    def stopped(self):
        return self._stopevent.is_set()

    def join(self, timeout=None):
        """ Stop the thread. """
        logger.debug('<-ActionThread-> Stopping thread {}...'.format(self.getName()))
        self._stopevent.set()
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
            print(self._interval)
            logger.debug('<-ActionThread-> {} running flash.'.format(self.getName()))
            self.flash()
        elif self._action_num == 6:
            logger.debug('<-ActionThread-> {} running breathe.'.format(self.getName()))
            self.breathe()
        elif self._action_num == 7:
            logger.debug('<-ActionThread-> {} running chase.'.format(self.getName()))
            self.chase()

    def solid_color(self):
        # color: like 'rgb(#, #, #)'
        c = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        for i in range(16):
            pixnum = i + 16 * (self._ringnum - 1)
            if self._order == 'RGB':
                #pixels[pixnum] = c
                pass
            else:
                #pixels[pixnum] = (c[1],c[0],c[2])
                pass
        #pixels.show()
        logger.debug('<-solid->   Ring:{} color:{}'.format(self._ringnum, c))

    def temp(self, source, test=False):
        # color: like 'rgb(#, #, #)'
        # source: 'h' for hotend 'b' for heatbed
        c = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        b = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))

        loop_counter = 2 # use to run a certain number of loops in when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            percent = self._printer.heatbedTemp if source == 'b' else self._printer.hotendTemp
            for i in range(16):
                pixnum = i + 16 * (self._ringnum - 1)
                if self._order == 'RGB':
                    #pixels[pixnum] = c if percent >= i/16 else b
                    pass
                else:
                    #pixels[pixnum] = (c[1],c[0],c[2]) if percent >= i/16 else (b[1], b[0], b[2])
                    pass
            #pixels.show()
            logger.debug('<-temp->    Ring:{} %:{} color:{} background:{}'.format(self._ringnum, percent, c, b))
            loop_counter = loop_counter - 1
            time.sleep(1) # update temp every 1 second

    def flash(self, test=False):
        # color1,2: like 'rgb(#, #, #)'
        c1 = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        c2 = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))

        loop_counter = 2 # use to run a certain number of loops in when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            for i in range(16):
                pixnum = i + 16 * (self._ringnum - 1)
                if self._order == 'RGB':
                    #pixels[pixnum] = c1
                    pass
                else:
                    #pixels[pixnum] = (c1[1],c1[0],c1[2])
                    pass
            #pixels.show()
            # swap colors
            c1, c2 = c2, c1
            time.sleep(self._interval)
            loop_counter = loop_counter - 1
            logger.debug('<-flash->   Ring:{} color:{}'.format(self._ringnum, c1))

    def breathe(self, test=False):
        # colors passed in as 'rgb(#, #, #)'
        c1 = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        c2 = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))

        num_steps = 100 # convenience for changing number of steps for color change
        # create easing instance for smoothing animations
        e = CubicEaseInOut(0, self._interval, num_steps) # will go from 0 to interval in num_steps steps
        loop_counter = 2 # use to run a certain number of loops in when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            last_sleep = 0
            for n in range(num_steps): # use 0.01 increment for color change (100 steps)
                t = n / num_steps if n > 0 else 0
                color = tuple(round(x + (y - x) * t) for x,y in zip(c1, c2)) # lerp between each color channel over increment
                #rt = r1 + (r2 - r1) * t
                #gt = g1 + (g2 - g1) * t
                #bt = b1 + (b2 - b1) * t
                for i in range(16): # set all pixels in this ring to current color
                    pixnum = i + 16 * (self._ringnum - 1)
                    if self._order == 'RGB':
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
            logger.debug('<-breathe-> Ring:{} color:{}'.format(self._ringnum, c1))
            c1, c2 = c2, c1
            loop_counter = loop_counter - 1

    def chase(self, test=False):
        # color passed in as 'rgb(#, #, #)'
        c = tuple(int(x.strip()) for x in self._color1[4:-1].split(','))
        b = tuple(int(x.strip()) for x in self._color2[4:-1].split(','))

        # creates easing instance for smoothing animations
        e = CubicEaseInOut(0, self._interval, 16) # will go from 0 to interval in 16 steps
        loop_counter = 2 # use to run a certain number of loops in when called with test True
        while True:
            if test is True and loop_counter <= 0:
                return
            if self.stopped():
                return
            last_sleep = 0
            for pos in range(16):
                for i in range(16): # step through all pixels in this ring
                    pixnum = i + 16 * (self._ringnum - 1)
                    if self._order == 'RGB':
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
            logger.debug('<-chase->   Ring:{} loop completed - chase color:{}'.format(self._ringnum, c))
            loop_counter = loop_counter - 1
