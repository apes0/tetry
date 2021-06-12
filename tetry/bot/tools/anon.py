import requests
from .urls import anonJoin

def anonAcc(name, captcha=None):
    json={'username':name}
    if captcha:
        json[captcha] = captcha
    return requests.post(anonJoin, json=json).json()