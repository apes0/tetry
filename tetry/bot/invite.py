class Invite:
    def __init__(self, data, bot):
        self.info = data
        self.roomId = data['roomid']
        self.sender = data['sender']
        self.name = data['roomname']
        self.bot = bot

    async def accept(self):
        await self.bot.joinRoom(self.roomId)
