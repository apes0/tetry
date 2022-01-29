import requests
from .urls import environment


def get_commit() -> str:
    json: dict = requests.get(environment).json()
    return json['signature']['commit']['id']
