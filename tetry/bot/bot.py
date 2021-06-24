import logging
import time
import copy
import requests

import trio
from trio_websocket import connect_websocket_url

from .chatMessage import ChatMessage
from .commands import new, resume, hello, authorize, presence, joinroom, createroom, ping, die
from .events import Event
from .ribbons import conn, connect, message, send, sendEv, getInfo
from .room import Room
from .frame import Frame
from .chatCommands import commandBot
from .urls import rooms

logger = logging.getLogger(__name__)

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs


@conn.addListener
async def heartbeat(bot):
    d = 5
    while True:
        ws = bot.ws
        await trio.sleep(d)
        try:
            await send(ping, ws)
            # note the time for the last sent ping, used to calculate the ping when we recive a pong
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
    await send(resume(sockid, resumeToken), ws)  # resume message
    # hello message
    await send(hello([message.message for message in bot.messages]), ws)


@message.addListener
async def _msgHandle(ws, msg):
    if msg == b'\x0c':  # ping
        bot = ws.bot
        ping = time.time() - bot.lastPing  # calculate the time it took to recive a pong
        bot.ping = ping
        await bot._trigger('pinged', ping)
        return
    await msgHandle(ws, msg)
#    print(msg)


async def msgHandle(ws, msg):
    bot = ws.bot
    if isinstance(msg, tuple):  # message with an id
        msg = msg[1]
    if isinstance(msg, list):  # multiple messages that should be handled
        for m in msg:
            await msgHandle(ws, m)
        return
    comm = msg['command']
    if 'id' in msg:  # log id'ed messages
        logServer(msg, ws)
    logger.info(f'got {comm} command')
    if comm == 'hello':
        bot.sockid = msg['id']
        bot.resume = msg['resume']
        messages = msg['packets']
        # get the raw json for the seen messages
        seen = [m.message for m in bot.serverMessages]
        for m in messages:
            if m not in seen:
                await msgHandle(ws, m)  # handle every unseen message
        # authorize message
        await send(authorize(bot.messageId, bot.token, bot.handling), ws)
    elif comm == 'authorize':
        await send(presence('online'), ws)  # set the presence
        await bot._trigger('ready')
    elif comm == 'migrate':
        await ws.aclose()  # close the connection to the websocket
        ws = msg['data']['endpoint']  # get the new endpoint
        await reconnect(ws, bot.sockid, bot.resume, bot.nurs, bot)  # reconnect
    elif comm == 'err':
        logger.error(msg['data'])  # log the error
    elif comm.startswith('gmupdate'):
        coms = comm.split('.')  # command and its subcommands
        if len(coms) == 1:  # only gmupdate
            oldRoom = bot.room
            room = Room(msg['data'], bot)  # create a new room object
            bot.room = room
            if not oldRoom:  # trigger the joined room event if the room was of None type
                await bot._trigger('joinedRoom', room)
        else:
            subcomm = coms[1]
            if subcomm == 'host':  # changed host
                bot.room.owner = msg['data']
                owner = bot.room.getPlayer(bot.room.owner)
                await bot._trigger('changeOwner', owner)
            elif subcomm == 'bracket':  # bracket change
                ind = bot.room._getIndex(msg['data']['uid'])
                bot.room.players[ind]['bracket'] = msg['data']['bracket']
                await bot._trigger('changeBracket', bot.room.players[ind])
            elif subcomm == 'leave':  # player leaving
                player = bot.room.getPlayer(msg['data'])
                bot.room.players.remove(player)
                await bot._trigger('userLeave', player)
            elif subcomm == 'join':  # player joining
                bot.room.players.append(msg['data'])
                await bot._trigger('userJoin', msg['data'])
    elif comm == 'chat':  # chat messages
        await bot._trigger('message', ChatMessage(msg['data']))
    elif comm == 'kick':  # kick message, sent only when there is a fatal error, similar to nope
        raise BaseException(msg['data']['reason'])
    elif comm == 'endmulti':  # end of game
        bot.room.inGame = False
        await bot._trigger('gameEnd')
    elif comm == 'startmulti':  # start of game
        bot.room.inGame = True
        await bot._trigger('gameStart')
    elif comm == 'replay':  # replay message
        for f in msg['data']['frames']:  # go through every frame
            fr = Frame(f)  # make a frame object
            if fr.type == 'start':  # if the type is 'start' change the bot listenId and note the time the game has started
                bot.room.listenId = msg['data']['listenID']
                bot.room.startTime = time.time()


@sendEv.addListener
# change the messageId for the bot if there is an id in the message we are sending
async def changeId(msg, ws):
    if isinstance(msg, bytes):
        return
    if 'id' in msg:
        ws.bot.messageId += 1
        log(msg, ws)  # log the message


class Message:
    def __init__(self, message):
        self.time = time.time()
        self.message = message

    def checkTime(self, t):
        return time.time() - self.time >= t


def log(msg, ws):
    bot = ws.bot
    messages = bot.messages
    messages.append(Message(msg))  # log the new message
    logFor = 30  # seconds
    for message in messages:
        remove = message.checkTime(logFor)
        if remove:
            messages.pop(0)  # remove the first message if needed
        else:
            break
    bot.messages = messages


def logServer(msg, ws):
    bot = ws.bot
    messages = bot.serverMessages
    messages.append(Message(msg))  # log the new message
    logFor = 30  # seconds
    for message in messages:
        remove = message.checkTime(logFor)
        if remove:
            messages.pop(0)  # remove the first message if needed
        else:
            break
    bot.serverMessages = messages

# bot class


events = [
    'ready',  # called after logging in
    'joinedRoom',  # called after joining a room
    'message',  # called when there is a chat message
    'changeBracket',  # called when a user changes their bracket
    'changeOwner',  # called when the owner is changed
    'userLeave',  # called when a user leaves
    'userJoin',  # called when a user joins
    'leftRoom',  # called after leaving a room
    # called when the game starts (when we get the startmulti message, not when we get a replay of type start)
    'gameStart',
    'gameEnd',  # called when the game ends (endmulti message)
    'pinged',  # called for every ping measurment
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
            self.events[event] = Event(event)  # event class for each event
        self.ping = 0  # seconds
        self.lastPing = None
        # command bot for chat commands
        self.commandBot = commandBot(self, commandPrefix)

    def run(self):
        trio.run(self._run)

    async def joinRoom(self, code: str):
        code = code.upper()
        await send(joinroom(code, self.messageId), self.ws)  # joinroom message

    async def createRoom(self, public: bool):
        # createroom message
        await send(createroom(public, self.messageId), self.ws)

    async def _run(self):
        self.user = getInfo(self.token)  # get info for the current user
        if self.user['role'] != 'bot':  # check if we aren't running on a bot account
            raise BaseException(
                'Your account is not a bot account, ask tetr.io support (support@tetr.io) for a bot account!')
        async with trio.open_nursery() as nurs:  # open a nursery
            conn.addListener(start)
            nurs.start_soon(connect, self, nurs)  # connect to the websocket
            self.nurs = nurs

    async def _trigger(self, event, *args):  # trigger an event
        await self.events[event].trigger(self.nurs, *args)

    def event(self, func):  # event decorator
        name = func.__name__
        if name.startswith('on_'):
            name = name[3:]
        self.events[name].addListener(func)

    def chatCommand(self, func):  # event decorator
        self.commandBot.register(func)

    async def stop(self):
        await send(die, self.ws)  # die message

    def getRooms(self):
        headers = {'authorization': f'Bearer {self.token}'}
        json = requests.get(rooms, headers=headers).json()
        if json['success']:
            return json['rooms']
        else:
            return json['errors'][0]['msg']

    def copy(self):
        return copy.deepcopy(self)  # make a deep copy of this class
