import logging
import time
import copy

import trio
from trio_websocket import connect_websocket_url

from .chatMessage import ChatMessage
from .commands import new, resume, hello, authorize, presence, joinroom, createroom, ping, die
from .events import Event
from .ribbons import conn, connect, message, send, sendEv, getInfo
from .room import Room
from .frame import Frame
from .chatCommands import commandBot

logger = logging.getLogger(__name__)

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
            bot.lastPing = time.time()
        except:
            return  # disconnected


async def start(bot):
    await send(new, bot.ws)
    conn.removeListener(start)


async def reconnect(ws, sockid, resumeToken, nurs, bot):
    ws = await connect_websocket_url(nurs, ws)
    ws.nurs = nurs
    ws.bot = bot
    bot.ws = ws
    await conn.trigger(nurs, bot)
    await send(resume(sockid, resumeToken), ws)
    await send(hello([message.message for message in bot.messages]), ws)


@message.addListener
async def _msgHandle(ws, msg):
    # ping
    if msg == b'\x0c':
        bot = ws.bot
        ping = time.time() - bot.lastPing
        bot.ping = ping
        await bot._trigger('pinged', ping)
    await msgHandle(ws, msg)
    print(msg)


async def msgHandle(ws, msg):
    bot = ws.bot
    if isinstance(msg, bytes):
        return
    elif isinstance(msg, tuple):
        msg = msg[1]
    if isinstance(msg, list):
        for m in msg:
            await msgHandle(ws, m)
        return
    comm = msg['command']
    if 'id' in msg:
        logServer(msg, ws)
    logging.info(f'got {comm} command')
    if comm == 'hello':
        bot.sockid = msg['id']
        bot.resume = msg['resume']
        messages = msg['packets']
        seen = [m.message for m in bot.serverMessages]
        for m in messages:
            if m not in seen:
                await msgHandle(ws, m)
        await send(authorize(bot.messageId, bot.token, bot.handling), ws)
    elif comm == 'authorize':
        await send(presence('online'), ws)
        await bot._trigger('ready')
    elif comm == 'migrate':
        await ws.aclose()
        ws = msg['data']['endpoint']
        await reconnect(ws, bot.sockid, bot.resume, bot.nurs, bot)
    elif comm == 'err':
        logger.error(msg['data'])
    elif comm.startswith('gmupdate'):
        coms = comm.split('.')
        if len(coms) == 1:  # only gmupdate
            oldRoom = bot.room
            room = Room(msg['data'], bot)
            bot.room = room
            if not oldRoom:
                await bot._trigger('joinedRoom', room)
        else:
            subcomm = coms[1]
            if subcomm == 'host':
                bot.room.owner = msg['data']
                owner = bot.room.getPlayer(bot.room.owner)
                await bot._trigger('changeOwner', owner)
            elif subcomm == 'bracket':
                ind = bot.room._getIndex(msg['data']['uid'])
                bot.room.players[ind]['bracket'] = msg['data']['bracket']
                await bot._trigger('changeBracket', bot.room.players[ind])
            elif subcomm == 'leave':
                player = bot.room.getPlayer(msg['data'])
                bot.room.players.remove(player)
                await bot._trigger('userLeave', player)
            elif subcomm == 'join':
                bot.room.players.append(msg['data'])
                await bot._trigger('userJoin', msg['data'])
    elif comm == 'chat':
        await bot._trigger('message', ChatMessage(msg['data']))
    elif comm == 'kick':
        raise BaseException(msg['data']['reason'])
    elif comm == 'endmulti':
        bot.room.inGame = False
        await bot._trigger('gameEnd')
    elif comm == 'startmulti':
        bot.room.inGame = True
        await bot._trigger('gameStart')
    elif comm == 'replay':
        for f in msg['data']['frames']:
            fr = Frame(f)
            if fr.type == 'start':
                bot.room.listenId = msg['data']['listenID']
                bot.room.startTime = time.time()


@sendEv.addListener
async def changeId(msg, ws):
    if isinstance(msg, bytes):
        return
    if 'id' in msg:
        ws.bot.messageId += 1
        log(msg, ws)


class Message:
    def __init__(self, message):
        self.time = time.time()
        self.message = message

    def checkTime(self, t):
        return time.time() - self.time >= t


def log(msg, ws):
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


def logServer(msg, ws):
    bot = ws.bot
    messages = bot.serverMessages
    messages.append(Message(msg))
    logFor = 30  # seconds
    for message in messages:
        remove = message.checkTime(logFor)
        if remove:
            messages.pop(0)
        else:
            break
    bot.serverMessages = messages

# bot class


events = [
    'ready',
    'joinedRoom',
    'message',
    'changeBracket',
    'changeOwner',
    'userLeave',
    'userJoin',
    'leftRoom',
    'gameStart',
    'gameEnd',
    'pinged',
]


class Bot:
    def __init__(self, token, commandPrefix='!'):
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
        self.serverMessages = []
        self.user = None
        for event in events:
            self.events[event] = Event(event)
        self.ping = 0  # seconds
        self.lastPing = None
        self.commandBot = commandBot(self, commandPrefix)

    def run(self):
        trio.run(self._run)

    async def joinRoom(self, code: str):
        code = code.upper()
        await send(joinroom(code, self.messageId), self.ws)

    async def createRoom(self, public: bool):
        await send(createroom(public, self.messageId), self.ws)

    async def _run(self):
        self.user = getInfo(self.token)
        if self.user['role'] != 'bot':
            raise BaseException(
                'Your account is not a bot account, ask tetrio support for a bot account!')
        async with trio.open_nursery() as nurs:
            conn.addListener(start)
            nurs.start_soon(connect, self, nurs)
            self.nurs = nurs

    async def _trigger(self, event, *args):
        await self.events[event].trigger(self.nurs, *args)

    def event(self, func):  # event decorator
        name = func.__name__
        if name.startswith('on_'):
            name = name[3:]
        self.events[name].addListener(func)

    def chatCommand(self, func):
        self.commandBot.register(func)

    async def stop(self):
        await send(die, self.ws)

    def copy(self):
        return copy.deepcopy(self)
