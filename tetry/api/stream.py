from .urls import stream

import requests

from .urls import addParam
from .cache import Cache


class Stream:
    def __init__(self, data):
        self.cache = Cache(data['cache'])
        data = data['data']['records']
        self.news = data


def getStream(stream):
    url = stream
    url = addParam(url, stream)
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise Exception(resp['error'])
    return Stream(resp)
