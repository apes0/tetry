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


def presence(id, status: str, detail: str):
    return {
        'command': 'social.presence',
        'id': id,
        'data': {
            'status': status,
            'detail': detail
        }
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


def leaveRoom(id):
    return {
        'id': id,
        'command': 'leaveroom',
        'data': False
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


def updateConfig(id, data):
    return {
        'id': id,
        'command': 'updateconfig',
        'data': data
    }


def replay(id, frames, listenId, frame):
    return {
        'command': 'replay',
        'data': {'frames': frames,
                 'listenID': listenId,
                 'provisioned': frame},
        'id': id
    }


def invite(id, uid):
    return {
        'id': id,
        'command': 'social.invite',
        'data': uid
    }


def removeFriend(id, uid):
    return (
        id,
        {
            'command': 'social.relationships.remove',
            'data': uid
        }
    )


def dm(id, uid, msg):
    return {
        'id': id,
        'command': 'social.dm',
        'data': {
            'recipient': uid,
            'msg': msg
        }
    }


def notificationAck(id):
    msg = {'command': 'social.notifications.ack'}
    if id:
        msg['data'] = id
    return msg
