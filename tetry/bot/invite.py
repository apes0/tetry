class Invite:
    def __init__(self, data, bot):
        print('invited')
        self.info = data
        self.roomId = data['roomid']
        self.sender = data['sender']
        self.name = data['roomname']
        self.bot = bot

    async def accept(self):
        if self.bot.room != None:
            await self.bot.room.leave()
        await self.bot.joinRoom(self.roomId)
