import time

import trio
from trio_websocket import connect_websocket_url

from .commands import *
from .room import Room
from .chatMessage import ChatMessage
from .events import Event
from .ribbons import conn, connect, message, send, sendEv

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs


# login


@conn.addListener
async def heartbeat(bot):
    d = 5
    while True:
        ws = bot.ws
        await trio.sleep(d)
        try:
            await send(ping, ws)
        except:
            return # disconnected


async def login(bot):
    await send(new, bot.ws)
    conn.removeListener(login)
    message.addListener(resp)


async def resp(ws, msg):
    bot = ws.bot
    if isinstance(msg, tuple):
        _ = msg[0]
        msg = msg[1]
    if isinstance(msg, bytes):
        return
    if isinstance(msg, list):
        for m in msg:
            print(m, len(msg))
            await resp(ws, m)
            return
    comm = msg['command']
    print(comm)
    if comm == 'hello':
        bot.sockid = msg['id']
        bot.resume = msg['resume']
        await send(authorize(bot.messageId, bot.token, bot.handling), ws)
    elif comm == 'authorize':
        await send(presence('online'), ws)
        await bot.events['ready'].trigger(ws.nurs)
    elif comm == 'chat':
        pass


async def reconnect(ws, sockid, resumeToken, nurs, bot):
    ws = await connect_websocket_url(nurs, ws)
    ws.nurs = nurs
    ws.bot = bot
    bot.ws = ws
    nurs.start_soon(conn.trigger, nurs, ws)
    await send(resume(sockid, resumeToken), ws)
    await send(hello([message.message for message in bot.messages]), ws)


@message.addListener
async def msgHandle(ws, msg):
    bot = ws.bot
    nurs = bot.nurs
    if isinstance(msg, bytes) or isinstance(msg, list):
        return
    if isinstance(msg, tuple):
        msg = msg[1]
    comm = msg['command']
    if comm == 'migrate':
        await ws.aclose()
        ws = msg['data']['endpoint']
        await reconnect(ws, bot.sockid, bot.resume, bot.nurs, bot)
    elif comm == 'err':
        raise Exception(msg['data'])
    elif comm == 'gmupdate':
        room = Room(msg['data'])
        bot.room = room
        await bot.events['joinedRoom'].trigger(nurs, room)
    elif comm == 'chat':
        await bot.events['message'].trigger(nurs, ChatMessage(msg['data']))


@sendEv.addListener
async def changeId(msg, ws):
    if isinstance(msg, bytes):
        return
    if 'id' in msg:
        ws.bot.messageId += 1
        await log(msg, ws)


class Message:
    def __init__(self, message):
        self.time = time.time()
        self.message = message

    def checkTime(self, t):
        return time.time() - self.time >= t


async def log(msg, ws):
    bot = ws.bot
    messages = bot.messages
    messages.append(Message(msg))
    logFor = 30  # seconds
    for message in messages:
        remove = message.checkTime(logFor)
        if remove:
            messages.pop(0)
        else:
            break
    bot.messages = messages

# bot class

events = [
    'ready',
    'joinedRoom',
    'message'
]


class Bot:
    def __init__(self, token):
        self.token = token
        self.room = None
        self.messageId = 0
        self.serverId = 0
        self.events = {}
        self.sockid = None
        self.resume = None
        self.messages = []
        self.handling = {
            'arr': 0,
            'das': 6,
            'sdf': 5,
            'safelock': True,
            'cancel': False,
            'dcd': 0,
        }
        self.nurs = None
        self.ws = None
        for event in events:
            self.events[event] = Event(event)

    def run(self):
        trio.run(self._run)

    async def joinRoom(self, code: str):
        code = code.upper()
        await send(joinroom(code, self.messageId), self.ws)

    async def createRoom(self, public: bool):
        await send(createroom(public, self.messageId), self.ws)

    async def _run(self):
        async with trio.open_nursery() as nurs:
            conn.addListener(login)
            nurs.start_soon(connect, self, nurs)
            self.nurs = nurs

    def event(self, func):  # event decorator
        name = func.__name__
        if name.startswith('on_'):
            name = name[3:]
        self.events[name].addListener(func)

    async def stop(self):
        await send(die, self.ws)

    async def send(self, message):
        await send(chat(message, self.messageId), self.ws)
