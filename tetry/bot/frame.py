class Frame:
    def __init__(self, data):
        self.type = data['type']
        self.frame = data['frame']
        if self.type in ['keydown', 'keyup']:
            self.key = data['data']['key']
            self.subframe = data['data']['subframe']
        else:  # no subframe for other events
            self.frame = data['frame']
            self.subframe = 0
