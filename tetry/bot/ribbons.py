import requests
from trio_websocket import open_websocket_url
import trio
import re

from .urls import *
from .message import pack, unpack
from .events import Event

def getCommit():
    regex = '"commit":{"id":"([0-9a-fA-F]*)"'
    headers = {"Range": "bytes=0-1000"} # get only the first 1000 bytes from tetrio
    text = requests.get(tetrioJs, headers=headers).text
    return re.search(regex, text).group(1)

async def send(data, ws=None):
    await ws.send_message(pack(data, ws))
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

async def connect(bot):
    token = bot.token
    ribbon = getRibbon(token)
    async with open_websocket_url(ribbon) as ws:
        ws.bot = bot
        await conn.trigger(ws)

message = Event()

@conn.addListener
async def heartbeat(ws):
    print('heartbeat')
    d = 5
    while True:
        await trio.sleep(d)
        await send(b'\x0B', ws)

@conn.addListener
async def reciver(ws):
    print('recv')
    while True:
        res = await ws.get_message()
        res = unpack(res)
        print(f'recived {res}')
        await message.trigger(ws, res)