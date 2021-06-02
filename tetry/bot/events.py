import trio


class Event:
    def __init__(self, name=None):
        self.name = name
        self.funcs = []

    async def trigger(self, *args):
        print(f'_trigger with {args}')
        async with trio.open_nursery() as nursery:
            for func in self.funcs:
                nursery.start_soon(func, *args)

    def addListener(self, func):
        print(f'add listener {func}')
        self.funcs.append(func)

    def removeListener(self, func):
        print(f'remove listener {func}')
        self.funcs.remove(func)