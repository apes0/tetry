import math

from .pieceRng import Rng


class Game:
    def __init__(self, config, seed):
        #        print(config.keys())
        self.config = config
        self.g = config['g']
        if self.g == 0:
            gFrames = math.inf
        else:
            gFrames = 1/self.g
        self.gFrames = gFrames
        self.gIncrease = config['gincrease']
        self.gMargin = config['gmargin']
        self.seed = seed
        self.rng = Rng(seed)
