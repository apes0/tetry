from urllib.parse import urlencode

base = 'https://ch.tetr.io/api' # base api url

stats = f'{base}/general/stats'
activity = f'{base}/general/activity'
user = f'{base}/users'
tetraLeague = f'{base}/users/lists/league'
fulltetraLeague = f'{tetraLeague}/all'
xp = f'{base}/users/lists/xp'
stream = f'{base}/streams'
news = f'{base}/news'

def getRankImage(rank):
    return f'https://tetr.io/res/league-ranks/{rank}.png'

def getAvatar(id):
    return f'https://tetr.io/user-content/avatars/{id}.jpg'

def recordUrl(username):
    return addParam(user, username) + '/records'

def addParam(url, param):
    url += f'/{param}'
    return url
    
def addQureyParam(url, params):
    url += f'?{urlencode(params)}'
    return url

def resolve(name):
    return f'https://tetr.io/api/users/{name}/resolve'
