import copy
import logging

import requests
import trio

from ..api.resolve import getId
from .chatCommands import commandBot
from .commands import (createroom, die, dm, invite, joinroom,
                       notificationAck, presence)
from .dm import Dm
from .events import Event
from .ribbons import Connection, getInfo
from .urls import dms, rooms, friend, unfriend
from .reconnect import reconnect

logger = logging.getLogger(__name__)

# api docs: https://github.com/Poyo-SSB/tetrio-bot-docs


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
    'migrated',  # called when the bot migrates to another worker
    'notification'  # called when the bot recives a notification
]


class Bot:
    def __init__(self, token, commandPrefix='!', handling=None, replayFrames=30, pingInterval=5):
        self.connection = None  # the connection to the server
        self.pingInterval = pingInterval  # interval between ping measurements
        self.replayFrames = replayFrames  # how many frames to send
        self.token = token  # bot token
        self.room = None  # room class
        self.messageId = 1  # message id for sending to the server
        self.serverId = 1  # server id
        self.events = {}  # events, each name has an event class representing it
        self.sockid = ''  # socket id
        self.resume = ''  # resume token
        self.messages = []  # messages sent
        defaultHandling = {
            'arr': 0,
            'das': 1,
            'sdf': 41,
            'safelock': True,
            'cancel': False,
            'dcd': 0,
        }
        # bot handling (effects playing only)
        self.handling = handling or defaultHandling
        self.nurs = None  # nursery
        self.serverMessages = []  # messages recived
        self.user = {}  # user info
        for event in events:
            self.events[event] = Event(event)  # event class for each event
        self.ping = 0  # seconds
        self.lastPing = 0  # when the last ping was sent
        # command bot for chat commands
        self.commandBot = commandBot(self, commandPrefix)  # command bot
        self.name = ''  # bot name
        self.id = ''  # bot id
        self.loggedIn = False  # bool showing if the bot is logged in
        self.onlineUsers = 0  # users online
        self.presences = []  # friend presences
        self.worker = {}  # websocket worker
        self.friends = []  # bot friends
        self.notifications = []  # notifications

    def run(self):
        trio.run(self._run)

    async def joinRoom(self, code: str):
        code = code.upper()
        if self.room != None:
            await self.room.leave()
        # joinroom message
        await self.connection.send(joinroom(code, self.messageId))

    async def createRoom(self, public: bool):
        # createroom message
        await self.connection.send(createroom(public, self.messageId))

    async def recconect(self, endpoint=None):
        await self.connection.close()
        endpoint = endpoint or self.connection.endpoint
        self.serverId = 1
        await reconnect(endpoint, self.sockid, self.resume, self.nurs, self)

    async def _run(self):
        self.user = getInfo(self.token)  # get info for the current user
        self.name = self.user['username']
        self.id = self.user['_id']
        if self.user['role'] != 'bot':  # check if we aren't running on a bot account
            raise BaseException(
                'Your account is not a bot account, ask tetr.io support (support@tetr.io) for a bot account!')
        async with trio.open_nursery() as nurs:  # open a nursery
            self.connection = Connection(self)  # create a connection
            # connect to the websocket
            nurs.start_soon(self.connection.connect, nurs)
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
        await self.connection.send(die)  # die message

    async def dm(self, msg, uid=None, name=None):
        if not uid and name:
            uid = getId(name, self.token)
        await self.connection.send(dm(self.messageId, uid, msg))  # dm message

    async def invite(self, uid=None, name=None):
        if not uid and name:
            uid = getId(name, self.token)
        # invite message
        await self.connection.send(invite(self.messageId, uid))

    async def setPresence(self, status, detail=''):
        # presence message
        await self.connection.send(presence(self.messageId, status, detail))

    async def notificationAck(self, id=None):
        # notification ack message
        await self.connection.send(notificationAck(id))

    def addFriend(self, uid=None, name=None):
        if not uid and name:
            uid = getId(name, self.token)
        headers = {'authorization': f'Bearer {self.token}'}
        json = requests.post(friend, headers=headers,
                             json={'user': uid}).json()
        if not json['success']:
            raise json['errors'][0]['msg']

    def removeFriend(self, uid=None, name=None):
        if not uid and name:
            uid = getId(name, self.token)
        headers = {'authorization': f'Bearer {self.token}'}
        json = requests.post(unfriend, headers=headers,
                             json={'user': uid}).json()
        if not json['success']:
            raise json['errors'][0]['msg']

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
