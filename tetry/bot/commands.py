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
                'commit': {
                    'id': getCommit()
                }
            }
        }
    }


die = {
    'command': 'die'
}

ping = b'\x0B'


def presence(status, detail=''):
    return {
        'command': 'social.presence',
        'status': status,
        'detail': detail
    }


def joinroom(room, id):
    return {
        'id': id,
        'command': 'joinroom',
        'data': room
    }


def createroom(public: bool, id):
    if public:
        public = 'public'
    else:
        public = 'private'
    return {
        'id': id,
        'command': 'createroom',
        'data': public
    }


def resume(sockId, resume):
    return {
        'command': 'resume',
        'socketid': sockId,
        'resumetoken': resume
    }


def hello(msgs):
    return {
        'command': 'hello',
        'packets': msgs
    }
