import requests

from .urls import resolve
from .exceptions import UserError


def get_id(name: str, token: str) -> str:
    name = name.lower()
    headers: dict = {'Authorization': f'Bearer {token}'}
    res: requests.Response = requests.get(
        resolve(name), headers=headers).json()
    if not res['success']:
        raise UserError(res['errors'][0]['msg'])
    return res['_id']
