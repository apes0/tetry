import requests
import websockets
import asyncio

from .urls import *
from .message import pack

class Connection:
    def __init__(self):
        pass


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

async def getSocket(token):
    ribbon = getRibbon(token)
    return await websockets.connect(ribbon)


# connect ->  reciver()
#             heartbeat()
# connect to a websocket and start a reciver and a heartbeat proccess

async def connect(token):
    socket = await getSocket(token)
    return await socket.connect()

async def heartbeat(ws):
    d = 5
    while True:
        send(ws, 0x0B)
        await asyncio.sleep(d)