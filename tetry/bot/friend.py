from ..api.user import get_user


class Friend:
    def __init__(self, data, bot):
        self.bot = bot
        self._id = data['_id']
        self._from = data['from']
        self._to = data['to']
        self.type = data['type']
        ids = [self._from['_id'], self._to['_id']]
        ids.remove(self.bot.id)
        self.id = ids[0]
        names = [self._from['username'], self._to['username']]
        names.remove(self.bot.name)
        self.name = names[0]

    def getPresence(self):
        return self.bot.presences.get(self.id)

    def getInfo(self):
        return get_user(self.id)

    def unfriend(self):
        self.bot.removeFriend(uid=self.id)

    async def dm(self, message):
        await self.bot.dm(message, uid=self.id)

    def getDms(self):
        return self.bot.getDms(self.id)

    async def invite(self):
        await self.bot.invite(uid=self.id)
