import requests

from .urls import recordUrl
from .cache import Cache


class Records:
    def __init__(self, data):
        self.cache = Cache(data['cache'])
        data = data['data']
        self.data = data
        self.zen = data['zen']
        self.blitz = data['records']['blitz']
        self._40l = data['records']['40l']
        self.records = {
            '40l': self._40l['record']['endcontext']['finalTime'],
            'bltz': self.blitz['record']['endcontext']['score'],
            'zen': self.zen['score']
        }


def getRecords(name):
    url = recordUrl(name.lower())
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise Exception(resp['error'])
    return Records(resp)
