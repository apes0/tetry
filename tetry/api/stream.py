import requests

from .urls import add_param, stream
from .cache import Cache
from .exceptions import StreamError


class Stream:
    '''
     Stream class for TETR.IO streams.
    '''

    def __init__(self, data: dict) -> None:
        self.cache = Cache(data['cache'])
        data = data['data']['records']
        self.news = data


def get_stream(stream_id: str) -> Stream:
    '''
    get_stream Return the given Stream from TETR.IO.

    :param stream_id: The id of the stream.
        Check https://tetr.io/about/api/#streamsstream for more info.
    :type stream_id: str
    :raises StreamError: Raises StreamError if the stream is not found.
    :return: The Stream object.
    :rtype: Stream
    '''
    url = stream
    url = add_param(url, stream_id)
    with requests.Session() as ses:
        resp = ses.get(url).json()
        if not resp['success']:
            raise StreamError(resp['error'])
    return Stream(resp)
