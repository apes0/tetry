class Check:
    def __init__(self, func):
        self.func = func  # check function

    def __call__(self, func):  # called when used as a decorator
        async def decorator(msg):
            if self.func(msg):
                await func(msg)

        decorator.__name__ = func.__name__
        return decorator


isOwner = Check(lambda msg: msg.user['_id'] == msg.bot.owner['id'])
isHost = Check(lambda msg: msg.user['_id'] == msg.bot.room.owner)
amHost = Check(lambda msg: msg.user['_id'] == msg.bot.id)
