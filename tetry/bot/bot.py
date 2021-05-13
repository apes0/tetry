from .ribbons import send, connect
from .events import Event

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs

events = [
    'recive',
    'open',
    'gameStart',
    'gameEnd',
    'start'
]

class Client:
    def __init__(self):
        self.token = None
        self.ws = None
        self.room = None
        self.endpoint = None
        self.events = {}
        for event in events:
            self.events[event] = Event(event)

    def send(self, data):
        send(self.ws, data)
    
    def event(self, func): # event decorator
        name = func.__name__
        if name.startswith('on_'):
            name = name[3:]
        self.events[name].addListener(func)

class Bot:
    def __init__(self, token):
        self.client = Client()
        self.token = token
    
    async def run(self):
        await connect(self.token)