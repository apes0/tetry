import requests

from .records import get_records
from .urls import add_param, add_query_param, get_avatar, get_rank_image, user
from .cache import Cache
from .exceptions import UserError


class User:
    def __init__(self, data):
        self.cache = Cache(data['cache'])
        data = data['data']['user']
        self.data = data
        self.id = data['_id']
        self.username = data['username']
        self.avatar_revision = data.get('avatar_revision') or None
        self.league = data['league']

    def get_pfp(self, rev=True):
        url = get_avatar(self.id)
        if rev and self.avatar_revision:
            url = add_query_param(url, {'rv': self.avatar_revision})
        return url

    def get_rank_image(self):
        return get_rank_image(self.data['league']['rank'])

    def get_records(self):
        return get_records(self.username)


def get_user(name, token=None):
    url = user
    url = add_param(url, name.lower())
    with requests.Session() as ses:
        headers = {'Authorization': f'Bearer {token}'} if token else None
        resp = ses.get(url, headers=headers).json()
        if not resp['success']:
            raise UserError(resp['error'])
    return User(resp)
