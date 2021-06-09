from .urls import room

class Room:
    def __init__(self, data):
        self.id = data['id']
        self.opts = data['game']['options']
        self.state = data['game']['state']
        self.match = data['game']['match']
        self.invite = room + self.id