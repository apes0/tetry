import requests
import websockets
import asyncio

from .urls import *
from .message import pack, unpack
from .events import Event

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
    ws = await websockets.connect(ribbon)
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
        print(res)
        await message.trigger(res)
        print('a')