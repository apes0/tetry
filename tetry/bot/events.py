import logging

logger = logging.getLogger(__name__)


class Event:
    def __init__(self, name=None, triggerOnce=False):
        self.name = name  # only used for debbuging
        self.funcs = []
        self.triggerOnce = triggerOnce
        if self.triggerOnce:
            self.triggered = False

    async def trigger(self, nurs, *args):
        if self.triggerOnce:
            if self.triggered:
                return
        logger.info(f'trigger {self.name} with {args}')
        for func in self.funcs:
            nurs.start_soon(func, *args)

    def addListener(self, func):
        logger.info(f'add listener {func}')
        self.funcs.append(func)

    def removeListener(self, func):
        logger.info(f'remove listener {func}')
        self.funcs.remove(func)
