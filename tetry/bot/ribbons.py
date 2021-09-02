import logging
import time

import requests
import trio
from trio_websocket import connect_websocket_url

from . import responses
from .commands import new, ping
from .events import Event
from .message import pack, unpack
from .urls import me, ribbon

logger = logging.getLogger(__name__)


async def msgHandle(ws, msg):
    bot = ws.bot
    if isinstance(msg, tuple):  # if the message has an id
        id = msg[0]
        bot.serverId += 1
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
        logger.info(f'unrecognized command {comm}')
        return
#    print(comm, func)
    await func(bot, msg, msgHandle)


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


async def send(data, connection):
    ws = connection.ws
    sendEv = connection.sendEv
    await sendEv.trigger(ws.nurs, data, ws, blocking=True)
#    print(f'^  {data}')
    data = pack(data)
#    print(data)
    await ws.send_message(data)
    logger.info(f'sent {data}')


def getInfo(token):
    headers = {'authorization': f'Bearer {token}'}  # oauth header
    res = requests.get(me, headers=headers)
    json = res.json()
    if json['success']:
        return json['user']
    else:
        raise BaseException(json['errors'][0]['msg'])


def getRibbon(token):
    headers = {'authorization': f'Bearer {token}'}  # oauth header
    res = requests.get(ribbon, headers=headers)
    json = res.json()
    if json['success']:
        return json['endpoint']  # endpoint from the api
    else:
        raise BaseException(json['errors'][0]['msg'])


# connect ->  receiver()
#             heartbeat()
# connect to a websocket and start a reciver and a heartbeat proccess
class Connection:
    def __init__(self, bot, endpoint=None, reconnected=False):
        self.bot = bot
        self.reconnected = reconnected
        self.pending = {}  # pending messages
        self.ws = None
        self.endpoint = endpoint
        self.closed = False

        # events
        sendEv = Event('sendEv', errorEvent=False)
        self.sendEv = sendEv
        conn = Event('conn', errorEvent=False)
        self.conn = conn
        # message event afetr sorting
        message = Event('message', errorEvent=False)
        self.message = message
        _message = Event('_message', errorEvent=False)  # message event
        self._message = _message

        # add event listeners

        _message.addListener(self.sortMessages)
        conn.addListener(self.reciver)
        sendEv.addListener(self.changeId)
        conn.addListener(self.heartbeat)
        message.addListener(self.msgHandle)

    async def send(self, data):
        try:
            await send(data, self)
        except:
            self.closed = True

    async def connect(self, nurs):
        token = self.bot.token
        ribbon = self.endpoint or getRibbon(token)
        ws = await connect_websocket_url(nurs, ribbon)  # connect to ribbon
        ws.nurs = nurs
        ws.bot = self.bot
        self.ws = ws
        self.bot.connection = self
        self.endpoint = ribbon
        if not self.reconnected:
            await self.send(new)
        await self.conn.trigger(nurs, self.bot)

    async def close(self):
        if not self.closed:
            await self.ws.aclose()
            self.closed = True

    async def reciver(self, _bot):
        while not self.closed:
            ws = self.ws
            try:
                res = await ws.get_message()
    #            print(res)
            except:
                self.closed = True
                return
            res = unpack(res)
#            print(f'v  {res}')
            logger.info(f'recived {res}')
            await self._message.trigger(ws.nurs, ws, res)

    async def sortMessages(self, ws, res):
        if not isinstance(res, tuple):
            await self.message.trigger(ws.nurs, ws, res)
            return
        bot = ws.bot
        sid = bot.serverId
        id = res[0]
        if id == sid + 1:
            await self.message.trigger(ws.nurs, ws, res)
            id += 1
        else:
            self.pending[id] = res
        while (msg := self.pending.get(id)):
            await self.message.trigger(ws.nurs, ws, msg)
            del self.pending[id]
            id += 1

    async def changeId(self, msg, ws):
        if isinstance(msg, bytes):
            return
        if 'id' in msg:
            ws.bot.messageId += 1
            log(msg, ws)  # log the message

    async def heartbeat(self, bot):
        while not self.closed:
            await self.send(ping)
            # note the time for the last sent ping, used to calculate the ping when we recive a pong
            bot.lastPing = time.time()
            await trio.sleep(bot.pingInterval)

    async def msgHandle(self, ws, msg):
        bot = ws.bot
        if msg == b'\x0c':  # pong
            ping = time.time() - bot.lastPing  # calculate the time it took to recive a pong
            bot.ping = ping
            await bot._trigger('pinged', ping)
            return
        await msgHandle(ws, msg)
    #    print(msg)
