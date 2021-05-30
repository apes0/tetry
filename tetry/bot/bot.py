from .ribbons import send, connect, message, conn
from .events import Event
import asyncio

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs


# login

async def login(ws):
    await send(ws, {'command':'new'})


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
    def __init__(self, token):
        self.client = Client()
        self.token = token
    
    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        print('_run')
        conn.addListener(login)
        await connect(self.token)
