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
    'T': 'print' # (changing tool, new in 1.17b)
}

class PrinterStatus:
    def __init__(self):
        self._hotendTemp = -1
        self._hotendTarget = -1
        self._heatbedTemp = -1
        self._heatbedTarget = -1
        self._percentComplete = -1
        self._state = ''

    # using property so retrieving temp will give percent complete as convenience
    @property
    def hotendTemp(self):
        if self._hotendTemp < 0 or self._hotendTarget < 0:
            return 0
        return self._hotendTemp / self._hotendTarget

    @hotendTemp.setter
    def hotendTemp(self, value):
        self._hotendTemp = value
    
    @property
    def hotendTarget(self):
        return 0 if self._hotendTarget < 0 else self._hotendTarget

    @hotendTarget.setter
    def hotendTarget(self, value):
        self._hotendTarget = value
    
    # using property so retrieving temp will give percent complete as convenience
    @property
    def heatbedTemp(self):
        if self._heatbedTemp < 0 or self._heatbedTarget < 0:
            return 0
        return self._heatbedTemp / self._heatbedTarget

    @heatbedTemp.setter
    def heatbedTemp(self, value):
        self._heatbedTemp = value
    
    @property
    def heatbedTarget(self):
        return 0 if self._heatbedTarget < 0 else self._heatbedTarget

    @heatbedTarget.setter
    def heatbedTarget(self, value):
        self._heatbedTarget = value

    @property
    def percentComplete(self):
        return 0 if self._percentComplete < 0 else self._percentComplete

    @percentComplete.setter
    def percentComplete(self, value):
        self._percentComplete = value

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        if value != self._state:
            self.handle_state_change(value)
        self._state = value
    
    def get_event(self):
        return state_events[self._state]
    
    def handle_state_change(self, newstate):
        print('State change detected!')
    
    def update_status(self, data):
        self.state = data['status']
        self.hotenedTemp = data['temps']['heads']['current'][0]
        self.hotendTarget = data['temps']['heads']['active'][0]
        self.heatbedTemp = data['temps']['bed']['current']
        self.heatbedTarget = data['temps']['bed']['active']
