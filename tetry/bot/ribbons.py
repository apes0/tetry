import re

import requests
import trio
from trio_websocket import connect_websocket_url

from .events import Event
from .message import pack, unpack
from .urls import *


def getCommit():
    regex = '"commit":{"id":"([0-9a-fA-F]*)"'
    # get only the first 1000 bytes from tetrio
    headers = {"Range": "bytes=0-1000"}
    text = requests.get(tetrioJs, headers=headers).text
    return re.search(regex, text).group(1)


sendEv = Event()


async def send(data, ws):
    await sendEv.trigger(ws.nurs, data, ws)
    data = pack(data)
    await ws.send_message(data)
    print(f'sent {data}')


def checkToken(token):
    headers = {'authorization': f'Bearer {token}'}
    res = requests.get(me, headers=headers)
    json = res.json()
    if json['success']:
        return json
    else:
        raise BaseException(json['errors'][0]['msg'])


def getRibbon(token):
    headers = {'authorization': f'Bearer {token}'}
    res = requests.get(ribbon, headers=headers)
    json = res.json()
    if json['success']:
        return json['endpoint']
    else:
        raise BaseException(json['errors'][0]['msg'])

# connect ->  receiver()
#             heartbeat()
# connect to a websocket and start a reciver and a heartbeat proccess


conn = Event()


async def connect(bot, nurs):
    token = bot.token
    ribbon = getRibbon(token)
    ws = await connect_websocket_url(nurs, ribbon)
    ws.nurs = nurs
    ws.bot = bot
    nurs.start_soon(conn.trigger, nurs, ws)
    await trio.sleep_forever()

message = Event()


@conn.addListener
async def reciver(ws):
    print('recv')
    while True:
        try:
            res = await ws.get_message()
        except:
            return  # disconnected
        res = unpack(res)
        print(f'recived {res}')
        await message.trigger(ws.nurs, ws, res)
