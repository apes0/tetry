from .ribbons import getCommit

new = {
    'command': 'new'
}


def authorize(msgid: int, token: str, handling: dict):
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


def presence(status: str, detail: str = ''):
    return {
        'command': 'social.presence',
        'status': status,
        'detail': detail
    }


def joinroom(room: str, id: int):
    return {
        'id': id,
        'command': 'joinroom',
        'data': room
    }


def createroom(public: bool, id: int):
    if public:
        public = 'public'
    else:
        public = 'private'
    return {
        'id': id,
        'command': 'createroom',
        'data': public
    }


def resume(sockId: str, resume: str):
    return {
        'command': 'resume',
        'socketid': sockId,
        'resumetoken': resume
    }


def hello(msgs: list):
    return {
        'command': 'hello',
        'packets': msgs
    }


def chat(msg: str, id: int):
    return {
        'id': id,
        'command': 'chat',
        'data': msg
    }


def switchBracket(id: int, bracket: str):
    return {
        'id': id,
        'command': 'switchbracket',
        'data': bracket
    }


def switchBracketHost(id: int, bracket: str, uid: str):
    return {
        'id': id,
        'command': 'switchbrackethost',
        'data': {
            'uid': uid,
            'bracket': bracket
        }
    }


def leaveRoom(id, room):
    return {
        'id': id,
        'command': 'leaveroom',
        'data': room
    }


def transferOwnership(id, uid):
    return {
        'id': id,
        'command': 'transferownership',
        'data': uid
    }


def kick(id, uid):
    return {
        'id': id,
        'command': 'kick',
        'data': uid
    }


def startRoom(id):
    return {
        'id': id,
        'command': 'startroom',
        'data': None
    }
