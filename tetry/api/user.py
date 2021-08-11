import requests

from .records import getRecords
from .urls import addParam, addQureyParam, getAvatar, getRankImage, user
from .cache import Cache


class User:
    def __init__(self, data):
        self.cache = Cache(data['cache'])
        data = data['data']['user']
        self.data = data
        self.id = data['_id']
        self.username = data['username']
        self.avatarRevision = data.get('avatar_revision') or None
        self.league = data['league']

    def getPfp(self, rev=True):
        url = getAvatar(self.id)
        if rev and self.avatarRevision:
            url = addQureyParam(url, {'rv': self.avatarRevision})
        return url

    def getRankImage(self):
        return getRankImage(self.data['league']['rank'])

    def getRecords(self):
        return getRecords(self.username)


def getUser(name):
    url = user
    url = addParam(url, name.lower())
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise Exception(resp['error'])
    return User(resp)
