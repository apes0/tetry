import asyncio


class Event:
    def __init__(self, name=None):
        self.name = name
        self.funcs = []

    def trigger(self, *args):
        asyncio.create_task(self._trigger(*args))

    async def _trigger(self, *args):
        funcs = [func(*args) for func in self.funcs]
        await asyncio.gather(*funcs)

    def addListener(self, func):
        self.funcs.append(func)

    def removeListener(self, func):
        self.funcs.remove(func)