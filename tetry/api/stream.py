import requests

from .urls import add_param, stream
from .cache import Cache
from .exceptions import StreamError


class Stream:
    def __init__(self, data: dict) -> None:
        self.cache = Cache(data['cache'])
        data = data['data']['records']
        self.news = data


def get_stream(stream_id: str) -> Stream:
    url = stream
    url = add_param(url, stream_id)
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise StreamError(resp['error'])
    return Stream(resp)
