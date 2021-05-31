from .ribbons import send, connect, message, conn
from .events import Event
from .commands import *
import asyncio

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs


# login

async def login(ws):
    await send(ws, new)
    message.addListener(resp)

async def resp(ws, msg):
    if isinstance(msg, tuple):
        msg = msg[1]
    comm = msg['command']
    if comm == 'hello':
        await send(ws, authorize(Bot.messageId, Bot.token, Bot.handling))
    elif comm == 'authorize':
        await send(ws, presence('online'))
        message.removeListener(resp)

#client and bot classes

events = []

class Client:
    def __init__(self):
        self.token = None
        self.room = None
        self.endpoint = None
        self.events = {}
        self.wsid = None
        self.resume = None
        self.requests = []
        for event in events:
            self.events[event] = Event(event)

    def event(self, func): # event decorator
        name = func.__name__
        if name.startswith('on_'):
            name = name[3:]
        self.events[name].addListener(func)

class Bot:
    messageId = 1
    handling = {
        'arr': 0,
        'das': 6,
        'sdf': 5,
        'safelock': True,
        'cancel': False,
        'dcd': 0,
    }
    token = ''
    def __init__(self, token):
        self.token = token
        Bot.token = token
    
    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        print('_run')
        conn.addListener(login)
        await connect(self.token)
