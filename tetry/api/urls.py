from urllib.parse import urlencode

base = 'https://ch.tetr.io/api'  # base api url

stats = f'{base}/general/stats'
activity = f'{base}/general/activity'
user = f'{base}/users'
tetraLeague = f'{base}/users/lists/league'
fullTetraLeague = f'{tetraLeague}/all'
xp = f'{base}/users/lists/xp'
stream = f'{base}/streams'
news = f'{base}/news'
environment = 'https://tetr.io/api/server/environment'


def get_rank_image(rank):
    return f'https://tetr.io/res/league-ranks/{rank}.png'


def get_avatar(id):
    return f'https://tetr.io/user-content/avatars/{id}.jpg'


def record_url(username):
    return add_param(user, username) + '/records'


def add_param(url, param):
    url += f'/{param}'
    return url


def add_query_param(url, params):
    url += f'?{urlencode(params)}'
    return url


def resolve(name):
    return f'https://tetr.io/api/users/{name}/resolve'
