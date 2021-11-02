new = {
    'command': 'new'
}

clearChat = {
    'command': 'clearchat'
}


def authorize(msgId: int, token: str, handling: dict, commit: str):
    return {
        'id': msgId,
        'command': 'authorize',
        'data': {
            'token': token,
            'handling': handling,
            'signature': {
                'commit': {
                    'id': commit
                }
            }
        }
    }


die = {
    'command': 'die'
}

ping = b'\x0B'


def presence(msgId, status: str, detail: str):
    return {
        'command': 'social.presence',
        'id': msgId,
        'data': {
            'status': status,
            'detail': detail
        }
    }


def joinroom(room: str, roomId: int):
    return {
        'id': roomId,
        'command': 'joinroom',
        'data': room
    }


def createroom(public: bool, msgId: int):
    if public:
        public = 'public'
    else:
        public = 'private'
    return {
        'id': msgId,
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


def chat(msg: str, msgId: int):
    return {
        'id': msgId,
        'command': 'chat',
        'data': msg
    }


def switchBracket(msgId: int, bracket: str):
    return {
        'id': msgId,
        'command': 'switchbracket',
        'data': bracket
    }


def switchBracketHost(msgId: int, bracket: str, uid: str):
    return {
        'id': msgId,
        'command': 'switchbrackethost',
        'data': {
            'uid': uid,
            'bracket': bracket
        }
    }


def leaveRoom(msgId):
    return {
        'id': msgId,
        'command': 'leaveroom',
        'data': False
    }


def transferOwnership(msgId, uid):
    return {
        'id': msgId,
        'command': 'transferownership',
        'data': uid
    }


def kick(msgId, uid, duration):
    return {
        'id': msgId,
        'command': 'kick',
        'data': {'uid': uid, 'duration': duration}
    }


def unban(msgId, name):
    return {'id': msgId,
            'command': 'unban',
            'data': name}


def startRoom(msgId):
    return {
        'id': msgId,
        'command': 'startroom',
        'data': None
    }


def updateConfig(msgId, data):
    return {
        'id': msgId,
        'command': 'updateconfig',
        'data': data
    }


def replay(msgId, frames, listenId, frame):
    return {
        'command': 'replay',
        'data': {'frames': frames,
                 'listenID': listenId,
                 'provisioned': frame},
        'id': msgId
    }


def invite(msgId, uid):
    return {
        'id': msgId,
        'command': 'social.invite',
        'data': uid
    }


def dm(msgId, uid, msg):
    return {
        'id': msgId,
        'command': 'social.dm',
        'data': {
            'recipient': uid,
            'msg': msg
        }
    }


def notificationAck(notif):
    msg = {'command': 'social.notifications.ack'}
    if notif:
        msg['data'] = notif
    return msg
