import requests

from .urls import news, add_param, add_query_param
from .cache import Cache
from .exceptions import NewsError


class News:
    def __init__(self, data: dict) -> None:
        self.cache = Cache(data['cache'])
        data = data['data']['news']
        self.news: dict = data


def get_news(stream=None, limit=25) -> News:
    url = news
    if stream:
        url = add_param(url, stream)
    url = add_query_param(url, {'limit': limit})
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise NewsError(resp['error'])
    return News(resp)
