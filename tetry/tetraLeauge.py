from .user import User
import requests
from .urls import tetraLeague, fulltetraLeague

def getTetraLeauge():
    with requests.Session() as ses:
        resp = ses.get(tetraLeague).json()
        if not resp['success']:
            raise Exception(resp['error'])
    json = resp['data']['users']
    out = []
    for user in json:
        out.append(User(user))
    return out

def getFullTetraLeauge():
    with requests.Session() as ses:
        resp = ses.get(fulltetraLeague).json()
        if not resp['success']:
            raise Exception(resp['error'])
    json = resp['data']['users']
    out = []
    for user in json:
        out.append(User(user))
    return out