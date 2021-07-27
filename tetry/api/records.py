import requests

from .urls import recordUrl


class Records:
    def __init__(self, data):
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
    json = resp['data']
    return Records(json)
