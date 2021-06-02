from .ribbons import send, connect, message, conn
from .events import Event
from .commands import *
import trio

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs


# login

async def login(ws):
    Bot.ws = ws
    await send(new, ws)
    message.addListener(resp)

async def resp(ws, msg):
    if isinstance(msg, tuple):
        msg = msg[1]
    comm = msg['command']
    if comm == 'hello':
        await send(authorize(Bot.messageId, Bot.token, Bot.handling), ws)
    elif comm == 'authorize':
        await send(presence('online'), ws)
        message.removeListener(resp)
        await Bot.events['ready'].trigger()

# bot class

events = [
    'ready'
    ]

class Bot:
    events = {}
    messageId = 0
    handling = {
        'arr': 0,
        'das': 6,
        'sdf': 5,
        'safelock': True,
        'cancel': False,
        'dcd': 0,
    }
    token = ''
    ws = None
    def __init__(self, token):
        self.token = token
        Bot.token = token
        self.room = ''
        for event in events:
            Bot.events[event] = Event(event)
    
    def run(self):
        trio.run(self._run)

    async def join(self, code):
        self.room = code
        await send(joinroom(code, Bot.messageId), Bot.ws)

    async def _run(self):
        print('_run')
        conn.addListener(login)
        await connect(self)

    def event(self, func): # event decorator
        name = func.__name__
        if name.startswith('on_'):
            name = name[3:]
        self.events[name].addListener(func)
    
    async def stop(self):
        await send(die, Bot.ws)