class ChatMessage:
    def __init__(self, data):
        self.content = data['content']
        self.safeContent = data['content_safe']
        self.user = data['user']
        self.system = data['system']