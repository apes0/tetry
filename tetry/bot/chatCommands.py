from .events import Event


class commandBot:
    def __init__(self, bot, prefix):
        # hook onto a bot to listen for its messages
        bot.events['message'].addListener(self.commandParser)
        self.commands = {}
        self.prefix = prefix
        self.bot = bot

    async def commandParser(self, msg):
        text = msg.content
        if text.startswith(self.prefix):
            text = text[len(self.prefix):]
            comm = text.split(' ')
            args = [msg]
            if len(comm) > 1:
                args += comm[1:]
            comm = comm[0]
            nurs = self.bot.nurs
            if comm in self.commands:
                await self.commands[comm].trigger(nurs, *args)

    def register(self, func):
        name = func.__name__
        event = Event(name)
        event.addListener(func)
        if name not in self.commands:
            self.commands[name] = event
        else:
            self.commands[name].addListener(func)
