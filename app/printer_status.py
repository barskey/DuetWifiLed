from app import logger

# Printer Status class to store current results from status requests
# Printer States:
state_events = {
    'C': 'config', # (configuration file is being processed)
    'I': 'idle', # (idle, no movement or code is being performed)
    'B': 'print', # (busy, live movement is in progress or a macro file is being run)
    'P': 'print', # (printing a file)
    'D': 'pause', # (decelerating, pausing a running print)
    'S': 'pause', # (stopped, live print has been paused)
    'R': 'pause', # (resuming a paused print)
    'H': 'error', # (halted, after emergency stop)
    'F': 'config', # (flashing new firmware)
    'T': 'print', # (changing tool, new in 1.17b)
    'O': 'config', # unknown
    'Z': 'complete' # special state used when changing from P to I
}

class PrinterStatus:
    def __init__(self):
        self._hotendTemp = -1
        self._hotendTarget = -1
        self._heatbedTemp = -1
        self._heatbedTarget = -1
        self._percentComplete = -1
        self._state = ''
        self._prev_state = ''
        self.needs_update = False
        self._tasks = [None for i in range(3)]
        self.last_status = ''
        
    # using property so retrieving temp will give percent complete as convenience
    @property
    def hotendTemp(self):
        if self._hotendTemp <= 0 or self._hotendTarget <= 0:
            return 0
        return self._hotendTemp / self._hotendTarget

    @hotendTemp.setter
    def hotendTemp(self, value):
        self._hotendTemp = value
    
    @property
    def hotendTarget(self):
        return 0 if self._hotendTarget <= 0 else self._hotendTarget

    @hotendTarget.setter
    def hotendTarget(self, value):
        self._hotendTarget = value
    
    # using property so retrieving temp will give percent complete as convenience
    @property
    def heatbedTemp(self):
        if self._heatbedTemp <= 0 or self._heatbedTarget <= 0:
            return 0
        return self._heatbedTemp / self._heatbedTarget

    @heatbedTemp.setter
    def heatbedTemp(self, value):
        self._heatbedTemp = value
    
    @property
    def heatbedTarget(self):
        return 0 if self._heatbedTarget <= 0 else self._heatbedTarget

    @heatbedTarget.setter
    def heatbedTarget(self, value):
        self._heatbedTarget = value

    @property
    def percentComplete(self):
        return 0 if self._percentComplete <= 0 else self._percentComplete

    @percentComplete.setter
    def percentComplete(self, value):
        self._percentComplete = value

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        if value != self._state:
            logger.debug('<-set state-> Printer state change detected!')
            # set to 'complete' state if changing to Idle from Print, else set to new state
            #if value == 'I': # if changing to idle
            #    if self._state == 'P': # if changing from P
            #        self._state = 'Z' # set to complete state instead of I
            #        self.needs_update = True
            #    elif self._state != 'Z': # but don't change to idle if print is complete
            #        self._state = value
            #        self.needs_update = True
            #else: # otherwise change to new state
            #    self._state = value
            #    self.needs_update = True

    def get_task(self, ringnum):
        return self._tasks[ringnum]

    def set_task(self, ringnum, task):
        self._tasks[ringnum] = task

    def get_event(self):
        return state_events[self._state]
    
    def update_status(self, data):
        self.last_status = str(data)
        self.state = data['status']
        self.hotendTemp = data['temps']['current'][1]
        self.hotendTarget = data['temps']['tools']['active'][0][0]
        self.heatbedTemp = data['temps']['current'][0]
        self.heatbedTarget = data['temps']['bed']['active']
        self.percentComplete = data['fractionPrinted']
    
    def get_status(self):
        return {
            'status': self.last_status,
            'state': self._state,
            'hotend': [self._hotendTemp, self._hotendTarget, self.hotendTemp],
            'bed': [self._heatbedTemp, self._heatbedTarget, self.heatbedTemp],
            'percent': self.percentComplete
        }

