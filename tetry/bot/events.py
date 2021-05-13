import asyncio


class Event:
    def __init__(self, name):
        self.name = name
        self.funcs = []

    async def trigger(self, *args):
        funcs = [func(*args) for func in self.funcs]
        await asyncio.gather(*funcs)

    def addListener(self, func):
        self.funcs.append(func)
