import requests

from .urls import record_url
from .cache import Cache
from .exceptions import RecordError


class Records:
    '''
     Records class for TETR.IO records.
     Provides 40 Lines, Blitz and Zen records.
    '''

    def __init__(self, data: dict) -> None:
        self.cache = Cache(data['cache'])
        data = data['data']
        self.data = data
        self.zen: dict = data['zen']
        self.blitz: dict = data['records']['blitz']
        self._40l: dict = data['records']['40l']
        self.records = {
            '40l': self._40l['record']['endcontext']['finalTime'],
            'blitz': self.blitz['record']['endcontext']['score'],
            'zen': self.zen['score']
        }


def get_records(name: str) -> Records:
    '''
    get_records Return records for a given player.

    :param name: The name of the player.
    :type name: str
    :raises RecordError: Raises RecordError if the player is not found.
    :return: The Records object with the records data.
    :rtype: Records
    '''
    url = record_url(name.lower())
    with requests.Session() as ses:
        resp: dict = ses.get(url).json()
        if not resp['success']:
            raise RecordError(resp['error'])
    return Records(resp)
