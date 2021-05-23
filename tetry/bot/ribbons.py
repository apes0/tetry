import requests
import websockets
import asyncio

from .urls import *
from .message import pack, unpack
from .events import Event

async def send(ws, data):
    await ws.send(pack(data))

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
    conn.trigger(ws)
    return ws

message = Event()

@conn.addListener
async def heartbeat(ws):
    d = 5
    while True:
        send(ws, 0x0B)
        await asyncio.sleep(d)

@conn.addListener
async def reciver(ws):
    while True:
        res = await ws.recv()
        print(unpack(res))
        message.trigger(res)