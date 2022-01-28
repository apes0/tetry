import requests

from .urls import resolve
from .exceptions import UserError


def get_id(name, token):
    name = name.lower()
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.get(resolve(name), headers=headers).json()
    if not res['success']:
        raise UserError(res['errors'][0]['msg'])
    return res['_id']
