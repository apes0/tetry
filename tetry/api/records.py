import requests

from .urls import record_url
from .cache import Cache
from .exceptions import RecordError


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
            'blitz': self.blitz['record']['endcontext']['score'],
            'zen': self.zen['score']
        }


def get_records(name):
    url = record_url(name.lower())
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise RecordError(resp['error'])
    return Records(resp)
