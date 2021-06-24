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
        if text.startswith(self.prefix):  # check if the message is a command
            text = text[len(self.prefix):]  # get the command
            comm = text.split(' ')  # get a list of the args
            args = [msg]  # function args
            if len(comm) > 1:
                args += comm[1:]  # add all command args if we have any
            comm = comm[0]  # get command name
            nurs = self.bot.nurs
            if comm in self.commands:  # check if we have a real command
                await self.commands[comm].trigger(nurs, *args)

    def register(self, func):
        name = func.__name__
        if name not in self.commands:  # add the func as a listener if the command exists, else make an event for it
            event = Event(name)  # create an event for the command
            event.addListener(func)
            self.commands[name] = event
        else:
            self.commands[name].addListener(func)
