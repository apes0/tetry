import requests

from .urls import news, addParam, addQureyParam
from .cache import Cache


class News:
    def __init__(self, data):
        self.cache = Cache(data['cache'])
        data = data['data']['news']
        self.news = data


def getNews(stream=None, limit=25):
    url = news
    if stream:
        url = addParam(url, stream)
    url = addQureyParam(url, {'limit': limit})
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise Exception(resp['error'])
    return News(resp)
