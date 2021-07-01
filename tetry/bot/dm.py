class Dm:
    def __init__(self, data):
        self.stream = data['stream']
        self.members = self.stream.split(':')
        msgData = data['data']
        self.system = msgData['system']
        self.content = msgData['content']
        if not self.system:  # system messages don't seem to have a content_safe key
            self.safeContent = msgData['content_safe']
        else:
            self.safeContent = self.content
        self.user = msgData['userdata']
        self.sender = msgData['user']
        self.ts = data['ts']
