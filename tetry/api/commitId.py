import requests
from .urls import environment


def get_commit():
    json = requests.get(environment).json()
    return json['signature']['commit']['id']
