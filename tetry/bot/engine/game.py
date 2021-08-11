import math

from .pieceRng import Rng
import trio
from .board import Board


class Game:
    def __init__(self, config, seed, bot):
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
        self.lockTime = config['locktime']
        self.seed = seed
        self.rng = Rng(seed)
        self.bag = []
        self.getBag()
        self.board = Board()
        self.piece = None
        self.bot = bot
#        bot.evnets['playing'].addListener(self.applyGravity)

    def getBag(self):
        self.bag = [*self.bag, *self.rng.getBag()]

    async def applyGravity(self):
        while self.bot.room.inGame:
            await trio.sleep_until(self.gFrames/60)
