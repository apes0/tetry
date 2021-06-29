import math

import trio

from .commands import replay
from .ribbons import send

minoTypes = ["z", "l", "o", "s", "i", "j", "t"]  # TODO: park miller prng


class Game:
    def __init__(self, data, bot):
        self.gameId = data['gameID']
        self.first = data['first']
        self.listenIds = {ctx['user']['_id']: ctx['listenID']
                          for ctx in data['contexts']}
        self.listenId = self.listenIds[bot.id]
        self.room = bot.room
        self.bot = bot
        self.startTime = 0
        self.pending = []

    def getFrame(self):
        passed = trio.current_time() - self.startTime
        frame = passed*60
        return {'frame': math.floor(frame), 'subframe': frame % 1}

    def press(self, key):
        f = self.getFrame()
        frame = f['frame']
        subframe = f['subframe']
        frame = {'frame': frame, 'type': 'keydown', 'data':
                 {
                     'key': key,
                     'subframe': subframe,
                 }
                 }
        self.pending.append(frame)

    def _sendStart(self):
        frame = {
            'frame': 0,
            'type': 'start',
            'data': {}
        }
        self.pending.append(frame)

    async def start(self):
        t = trio.current_time()
        self.startTime = t
        d = 30  # frames
        frame = 0  # frames
        while self.bot.room.inGame:
            t += d/60
            frame += d
            await trio.sleep_until(t)
            await send(replay(self.bot.messageId, self.pending, self.gameId, frame), self.bot.ws)
            self.pending = []
