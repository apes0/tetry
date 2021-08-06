import copy
import logging
import time

import requests
import trio

from ..api.resolve import getId
from . import responses
from .chatCommands import commandBot
from .commands import (createroom, die, dm, invite, joinroom, new,
                       notificationAck, ping, presence, removeFriend)
from .dm import Dm
from .events import Event
from .ribbons import conn, connect, getInfo, message, send, sendEv
from .urls import dms, rooms

logger = logging.getLogger(__name__)

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs


@conn.addListener
async def heartbeat(bot):
    await send(new, bot.ws)
    while True:
        ws = bot.ws
        await trio.sleep(bot.pingInterval)
        try:
            await send(ping, ws)
            # note the time for the last sent ping, used to calculate the ping when we recive a pong
            bot.lastPing = time.time()
        except:
            return  # disconnected


@message.addListener
async def _msgHandle(ws, msg):
    bot = ws.bot
    if msg == b'\x0c':  # ping
        ping = time.time() - bot.lastPing  # calculate the time it took to recive a pong
        bot.ping = ping
        await bot._trigger('pinged', ping)
        return
    await msgHandle(ws, msg)
#    print(msg)


async def msgHandle(ws, msg):
    bot = ws.bot
    if isinstance(msg, tuple):  # if the message has an id
        id = msg[0]
        bot.serverId = max(id, bot.serverId)
        msg = msg[1]
        msg['id'] = id
        logServer(msg, ws)
    if isinstance(msg, list):  # multiple messages that should be handled
        for m in msg:
            await msgHandle(ws, m)
        return
#    print(f'parsing command {msg["command"]}')
    comm = msg['command'].split('.')[0]
#    print(comm)
    logger.info(f'got {comm} command')
    try:
        func = responses.__dict__[comm]
    except:
        return
#    print(comm, func)
    await func(bot, msg, msgHandle)


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
        self.id = message['id']
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
    #    print(f'logging message {msg}')
    bot = ws.bot
    messages = bot.serverMessages
    messages.append(Message(msg))  # log the new message
    logFor = 30  # seconds
    for message in messages:
        if message.checkTime(logFor):
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
    'playing',  # called when you can play
    'invited',  # called when you get invited to join a room, you can accept or ignore the invite
    'dm',  # called when you get a dm
]


class Bot:
    def __init__(self, token, commandPrefix='!', handling=None, replayFrames=30, pingInterval=5):
        self.pingInterval = pingInterval  # interval between ping measurements
        self.replayFrames = replayFrames  # how many frames to send
        self.token = token  # bot token
        self.room = None  # room class
        self.messageId = 1  # message id for sending to the server
        self.serverId = 0  # server id
        self.events = {}  # events, each name has an event class representing it
        self.sockid = None  # socket id
        self.resume = None  # resume token
        self.messages = []  # messages sent
        if not handling:
            handling = {
                'arr': 0,
                'das': 1,
                'sdf': 41,
                'safelock': True,
                'cancel': False,
                'dcd': 0,
            }
        self.handling = handling  # bot handling (effects playing only)
        self.nurs = None  # nursery
        self.ws = None  # websocket
        self.serverMessages = []  # messages recived
        self.user = None  # user info
        for event in events:
            self.events[event] = Event(event)  # event class for each event
        self.ping = 0  # seconds
        self.lastPing = None  # when the last ping was sent
        # command bot for chat commands
        self.commandBot = commandBot(self, commandPrefix)  # command bot
        self.name = None  # bot name
        self.id = None  # bot id
        self.loggedIn = False  # bool showing if the bot is logged in
        self.onlineUsers = 0  # users online
        self.presences = []  # friend presences
        self.worker = None  # websocket worker
        self.friends = []  # bot friends

    def run(self):
        trio.run(self._run)

    async def joinRoom(self, code: str):
        code = code.upper()
        if self.room != None:
            await self.room.leave()
        await send(joinroom(code, self.messageId), self.ws)  # joinroom message

    async def createRoom(self, public: bool):
        # createroom message
        await send(createroom(public, self.messageId), self.ws)

    async def _run(self):
        self.user = getInfo(self.token)  # get info for the current user
        self.name = self.user['username']
        self.id = self.user['_id']
        if self.user['role'] != 'bot':  # check if we aren't running on a bot account
            raise BaseException(
                'Your account is not a bot account, ask tetr.io support (support@tetr.io) for a bot account!')
        async with trio.open_nursery() as nurs:  # open a nursery
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

    async def dm(self, msg, uid=None, name=None):
        if not uid and name:
            uid = getId(name, self.token)
        await send(dm(self.messageId, uid, msg), self.ws)  # dm message

    async def invite(self, uid=None, name=None):
        if not uid and name:
            uid = getId(name, self.token)
        await send(invite(self.messageId, uid), self.ws)  # invite message

    async def setPresence(self, status, detail=''):
        # presence message
        await send(presence(self.messageId, status, detail), self.ws)

    async def notificationAck(self, id=None):
        await send(notificationAck(id), self.ws)  # notification ack message

    def getDms(self, uid):
        res = []
        headers = {'authorization': f'Bearer {self.token}'}
        _dms = requests.get(dms + uid, headers=headers).json()
        if not _dms['success']:
            raise _dms['errors'][0]['msg']
        for d in _dms['dms']:
            res.append(Dm(d))
        return res

    def getRooms(self):
        headers = {'authorization': f'Bearer {self.token}'}
        json = requests.get(rooms, headers=headers).json()
        if not json['success']:
            raise json['errors'][0]['msg']
        return json['rooms']

    def copy(self):
        return copy.deepcopy(self)  # make a deep copy of this class
