class ChatMessage:
    def __init__(self, data, bot):
        self.system = data['system']
        self.content = data['content']
        if not self.system:  # system messages don't seem to have a content_safe key
            self.safeContent = data['content_safe']
        else:
            self.safeContent = self.content
        self.user = data['user']
        self.bot = bot
