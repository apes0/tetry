import copy
import logging
import time

import requests
import trio

from . import responses
from .chatCommands import commandBot
from .commands import (createroom, die, dm, invite, joinroom, new, ping,
                       presence, removeFriend)
from .dm import Dm
from .events import Event
from .ribbons import conn, connect, getInfo, message, send, sendEv
from .urls import dms, rooms

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
    comm = msg['command'].split('.')[0]
#    print(comm)
    if 'id' in msg:  # log id'ed messages
        logServer(msg, ws)
    logger.info(f'got {comm} command')
    if comm not in responses.__dict__:
        return
    func = responses.__dict__[comm]
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
    'playing',  # called when you can play
    'invited',  # called when you get invited to join a room, you can accept or ignore the invite
    'dm',  # called when you get a dm
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
        self.name = None
        self.id = None
        self.loggedIn = False
        self.onlineUsers = 0

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
        self.name = self.user['username']
        self.id = self.user['_id']
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

    async def dm(self, uid, msg):
        await send(dm(self.messageId, uid, msg), self.ws)  # die message

    async def invite(self, uid):
        await send(invite(self.messageId, uid), self.ws)  # die message

    async def removeFriend(self, uid):
        await send(removeFriend(self.messageId, uid), self.ws)  # die message

    async def setPresence(self, status, detail=''):
        await send(presence(self.messageId, status, detail), self.ws)

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
