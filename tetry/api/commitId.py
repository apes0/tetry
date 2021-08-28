import requests
from .urls import enviorment


def getCommit():
    json = requests.get(enviorment).json()
    return json['signature']['commit']['id']
