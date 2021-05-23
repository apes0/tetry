from .ribbons import send, connect, message
from .events import Event
import asyncio

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs

events = [
    'recive',
    'send'
]

class Client:
    def __init__(self):
        self.token = None
        self.ws = None
        self.room = None
        self.endpoint = None
        self.events = {}
        self.wsid = None
        self.resume = None
        self.requests = []
        for event in events:
            self.events[event] = Event(event)

    async def send(self, data):
        await send(self.ws, data)
    
    @message.addListener
    async def login(self, msg):
        self.wsid = msg['id']
        self.resume = msg['resume']
        self.requests.append(msg)
    
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
        ws = await connect(self.token)
        self.client.ws = ws
        self.ws = ws
        await self.send({'command':'new'})

    async def send(self, data):
        await self.client.send(data)
