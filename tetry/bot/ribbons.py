import logging
import time

import requests
import trio
from trio_websocket import connect_websocket_url, ConnectionClosed


from . import responses
from .commands import new, ping, hello, resume
from .events import Event
from .message import pack, unpack
from .urls import me, ribbon

logger = logging.getLogger(__name__)


class Message:
    def __init__(self, message):
        self.time = time.time()
        self.id = message['id']
        self.message = message

    def checkTime(self, t):
        return time.time() - self.time >= t


async def send(data, connection):
    ws = connection.ws
    sendEv = connection.sendEv
    await sendEv.trigger(connection.nurs, data, blocking=True)
#    print(f'^  {data}')
    data = pack(data)
#    print(data)
    try:
        await ws.send_message(data)
    except ConnectionClosed:
        disconnected = False
        if not connection.closed:
            disconnected = True
            connection.closed = True
        await connection.closedEv.trigger(connection.nurs, disconnected)
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
    def __init__(self, bot, endpoint=None):
        self.bot = bot
        self.pending = {}  # pending messages
        self.ws = None
        self.endpoint = endpoint
        self.closed = False
        self.nurs = None

        # events
        sendEv = Event('sendEv', errorEvent=False)
        self.sendEv = sendEv
        conn = Event('conn', errorEvent=False)
        self.conn = conn
        closedEv = Event('closedEv', errorEvent=False)
        self.closedEv = closedEv
        # message event before sorting
        _message = Event('_message', errorEvent=False)
        self._message = _message
        # message event afetr sorting
        message = Event('message', errorEvent=False)
        self.message = message

        # add event listeners

        _message.addListener(self.sortMessages)
        conn.addListener(self.reciver)
        sendEv.addListener(self.changeId)
        conn.addListener(self.heartbeat)
        message.addListener(self._msgHandle)

    async def send(self, data):
        await send(data, self)

    async def connect(self, nurs):
        await self._connect(nurs)
        await self.send(new)

    async def _connect(self, nurs, endpoint=None):
        self.closed = False
        token = self.bot.token
        ribbon = endpoint or getRibbon(token)
        ws = await connect_websocket_url(nurs, ribbon)  # connect to ribbon
        self.nurs = nurs
        self.ws = ws
        self.bot.connection = self
        self.endpoint = ribbon
        await self.conn.trigger(nurs, self.bot)

    async def close(self):
        if not self.closed:
            await self.ws.aclose()
            self.closed = True
            await self.closedEv.trigger(self.nurs, False)

    async def reciver(self, _bot):
        while not self.closed:
            ws = self.ws
            try:
                res = await ws.get_message()
    #            print(res)
            except ConnectionClosed:
                disconnected = False
                if not self.closed:
                    disconnected = True
                    self.closed = True
                await self.closedEv.trigger(self.nurs, disconnected)
                return
            res = unpack(res)
#            print(f'v  {res}')
            logger.info(f'recived {res}')
            await self._message.trigger(self.nurs, res)

    async def sortMessages(self, res):
        if not isinstance(res, tuple):
            await self.message.trigger(self.nurs, res)
            return
        bot = self.bot
        sid = bot.serverId
        msgId = res[0]
        if msgId == sid + 1:
            await self.message.trigger(self.nurs, res)
            msgId += 1
        else:
            self.pending[msgId] = res
        while (msg := self.pending.get(msgId)):
            await self.message.trigger(self.nurs, msg)
            del self.pending[msgId]
            msgId += 1

    async def reconnect(self, ws, sockid, resumeToken):
        await self.close()
        await self._connect(self.nurs, ws)
        await self.send(resume(sockid, resumeToken))  # resume message
        # hello message
        await self.send(hello([message.message for message in self.bot.messages]))

    async def changeId(self, msg):
        if isinstance(msg, bytes):
            return
        if 'id' in msg:
            self.bot.messageId += 1
            self.log(msg)  # log the message

    async def ping(self):
        await self.send(ping)
        # note the time for the last sent ping, used to calculate the ping when we recive a pong
        self.bot.lastPing = time.time()

    async def heartbeat(self, bot):
        while not self.closed:
            await self.ping()
            await trio.sleep(bot.pingInterval)

    async def _msgHandle(self, msg):
        bot = self.bot
        if msg == b'\x0c':  # pong
            ping = time.time() - bot.lastPing  # calculate the time it took to recive a pong
            bot.ping = ping
            await bot._trigger('pinged', ping)
            return
        await self.msgHandle(msg)
    #    print(msg)

    async def msgHandle(self, msg):
        bot = self.bot
        if isinstance(msg, tuple):  # if the message has an id
            msgId = msg[0]
            bot.serverId += 1
            msg = msg[1]
            msg['id'] = msgId
            self.logServer(msg)
        if isinstance(msg, list):  # multiple messages that should be handled
            for m in msg:
                await self.msgHandle(m)
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
        await func(bot, msg, self.msgHandle)

    def log(self, msg):
        bot = self.bot
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

    def logServer(self, msg):
        #    print(f'logging message {msg}')
        bot = self.bot
        messages = bot.serverMessages
        messages.append(Message(msg))  # log the new message
        logFor = 30  # seconds
        for message in messages:
            if message.checkTime(logFor):
                messages.pop(0)  # remove the first message if needed
            else:
                break
        bot.serverMessages = messages
