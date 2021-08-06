import logging

import requests
from trio_websocket import connect_websocket_url

from .events import Event
from .message import pack, unpack
from .urls import enviorment, me, ribbon

logger = logging.getLogger(__name__)


def getCommit():
    json = requests.get(enviorment).json()
    return json['signature']['commit']['id']


sendEv = Event('sendEv')


async def send(data, ws):
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


conn = Event('conn')


async def connect(bot, nurs):
    token = bot.token
    ribbon = getRibbon(token)
    ws = await connect_websocket_url(nurs, ribbon)  # connect to ribbon
    ws.nurs = nurs
    ws.bot = bot
    bot.ws = ws
    nurs.start_soon(conn.trigger, nurs, bot)

message = Event('message')


@conn.addListener
async def reciver(bot):
    while True:
        try:
            ws = bot.ws
            res = await ws.get_message()
        except:
            return  # disconnected
        res = unpack(res)
#        print(f'v  {res}')
        logger.info(f'recived {res}')
        await message.trigger(ws.nurs, ws, res)
