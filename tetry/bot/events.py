import asyncio


class Event:
    def __init__(self, name=None):
        self.name = name
        self.funcs = []

    async def trigger(self, *args):
        print(f'_trigger with {args}')
        funcs = [func(*args) for func in self.funcs]
        print(funcs, args)
        await asyncio.gather(*funcs)

    def addListener(self, func):
        print(f'add listener {func}')
        self.funcs.append(func)

    def removeListener(self, func):
        print(f'remove listener {func}')
        self.funcs.remove(func)