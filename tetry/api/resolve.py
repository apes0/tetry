import requests

from .urls import resolve


def getId(name, token):
    headers = {'authorization': f'Bearer {token}'}
    res = requests.get(resolve(name), headers=headers).json()
    if not res['success']:
        raise BaseException(res['errors'][0]['msg'])
    return res['_id']
