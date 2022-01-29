import requests

from .urls import news, add_param, add_query_param
from .cache import Cache
from .exceptions import NewsError


class News:
    '''
     News class for TETR.IO news.
    '''

    def __init__(self, data: dict) -> None:
        self.cache = Cache(data['cache'])
        data = data['data']['news']
        self.news: dict = data


def get_news(stream: str = None, limit=25) -> News:
    '''
    get_news Get news from TETR.IO news, optionally filtered by stream.

    :param stream: The stream to filter news by.
        Check https://tetr.io/about/api/#streamsstream, defaults to None
    :type stream: str, optional
    :param limit: News length limit, defaults to 25
    :type limit: int, optional
    :raises NewsError: Raises NewsError if the news is not found.
    :return: The News object with the news data.
    :rtype: News
    '''
    url = news
    if stream:
        url = add_param(url, stream)
    url = add_query_param(url, {'limit': limit})
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise NewsError(resp['error'])
    return News(resp)
