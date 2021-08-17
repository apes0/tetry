class Notification:
    def __init__(self, data, bot):
        self.bot = bot
        self.id = data['_id']
        self.seen = data['seen']
        self.type = data['type']
        self.stream = data['stream']
        self.data = data['data']
        self.ts = data['ts']

    def acknoledge(self):
        self.seen = True
        self.bot.notificationAck(self.id)
