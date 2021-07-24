from .pieceRng import Rng


class Game:
    def __init__(self, config, seed):
        #        print(config.keys())
        self.config = config
        self.g = config['g']
        self.gFrames = 1/self.g
        self.gIncrease = config['gincrease']
        self.gMargin = config['gmargin']
        self.seed = seed
        self.rng = Rng(seed)
