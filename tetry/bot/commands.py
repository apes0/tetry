from .ribbons import getCommit

new = {
    'command': 'new'
}


def authorize(msgid:int, token:str, handling:dict):
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


def presence(status:str, detail:str=''):
    return {
        'command': 'social.presence',
        'status': status,
        'detail': detail
    }


def joinroom(room:str, id:int):
    return {
        'id': id,
        'command': 'joinroom',
        'data': room
    }


def createroom(public: bool, id:int):
    if public:
        public = 'public'
    else:
        public = 'private'
    return {
        'id': id,
        'command': 'createroom',
        'data': public
    }


def resume(sockId:str, resume:str):
    return {
        'command': 'resume',
        'socketid': sockId,
        'resumetoken': resume
    }


def hello(msgs:list):
    return {
        'command': 'hello',
        'packets': msgs
    }


def chat(msg:str, id:int):
    return {
        'id': id,
        'command': 'chat',
        'data': msg
    }