from .ribbons import getCommit

new = {
    'command': 'new'
}

def authorize(msgid, token, handling):
    return {
        'id': msgid,
        'command': 'authorize',
        'data': {
            'token': token,
            'handling': handling,
            'signature': {
                'commit':{
                    'id': getCommit()
                    }
                }
            }
        }

die = {
    'command': 'die'
}

ping = 0x0B

def presence(status, detail=''):
    return {
        'command': 'social.presence',
        'status': status,
        'detail': detail
    }