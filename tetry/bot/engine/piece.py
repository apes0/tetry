from yarg import get
from .pieces import pieces
from .spawnLocation import getLocation


class Piece:
    def __init__(self, type):
        self.type = type
        self.shape = pieces[type]
        self.y = 20
        self.x = getLocation(self.shape)
