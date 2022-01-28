import requests

from .urls import add_param
from .cache import Cache
from .exceptions import StreamError


class Stream:
    def __init__(self, data):
        self.cache = Cache(data['cache'])
        data = data['data']['records']
        self.news = data


def get_stream(stream):
    url = stream
    url = add_param(url, stream)
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise StreamError(resp['error'])
    return Stream(resp)
