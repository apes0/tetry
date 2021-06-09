class Event:
    def __init__(self, name=None, triggerOnce=False):
        self.name = name # only used for debbuging
        self.funcs = []
        self.triggerOnce = triggerOnce
        if self.triggerOnce:
            self.triggered = False

    async def trigger(self, nurs, *args):
        if self.triggerOnce:
            if self.triggered:
                return
        print(f'trigger {self.name} with {args}')
        for func in self.funcs:
            nurs.start_soon(func, *args)

    def addListener(self, func):
        print(f'add listener {func}')
        self.funcs.append(func)

    def removeListener(self, func): # TODO: fix this
        print(f'remove listener {func}')
        self.funcs.remove(func)
