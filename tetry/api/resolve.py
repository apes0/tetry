import requests

from .urls import resolve
from .exceptions import UserError


def get_id(name: str, token: str) -> str:
    '''
    get_id Get the ID of a user.

    :param name: The name of the user.
    :type name: str
    :param token: Your bot's token.
    :type token: str
    :raises UserError: Raises UserError if the user is not found.
    :return: The ID of the user.
    :rtype: str
    '''
    name = name.lower()
    headers: dict = {'Authorization': f'Bearer {token}'}
    res: requests.Response = requests.get(
        resolve(name), headers=headers).json()
    if not res['success']:
        raise UserError(res['errors'][0]['msg'])
    return res['_id']
