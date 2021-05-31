import requests
import websockets
import asyncio
import re

from .urls import *
from .message import pack, unpack
from .events import Event

def getCommit():
    url = 'https://tetr.io/tetrio.js'
    regex = '"commit":{"id":"([0-9a-fA-F]*)"'
    headers = {"Range": "bytes=0-1000"} # get only the first 1000 bytes from tetrio
    text = requests.get(url, headers=headers).text
    return re.search(regex, text).group(1)

async def send(ws, data):
    print('send')
    await ws.send(pack(data))
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

async def connect(token):
    ribbon = getRibbon(token)
    ws = await websockets.connect(ribbon, ping_interval=None, ssl=True)
    await conn.trigger(ws)

message = Event()

@conn.addListener
async def heartbeat(ws):
    print('heartbeat')
    d = 5
    while True:
        await asyncio.sleep(d)
        await send(ws, 0x0B)

@conn.addListener
async def reciver(ws):
    print('recv')
    while True:
        res = await ws.recv()
        res = unpack(res)
        print(f'recived {res}')
        await message.trigger(ws, res)