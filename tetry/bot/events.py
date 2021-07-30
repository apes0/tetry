import logging

logger = logging.getLogger(__name__)


class Event:
    def __init__(self, name=None, triggerOnce=False):
        self.name = name  # only used for debbuging
        self.funcs = []
        self.triggerOnce = triggerOnce
        if self.triggerOnce:
            self.triggered = False

    # trigger event with args, runs using a nursery supplied from the run func
    async def trigger(self, nurs, *args, blocking=False):
        if self.triggerOnce and self.triggered:  # check if we can be triggered more than once
            return
        logger.info(f'trigger {self.name} with {args}')
        for func in self.funcs:
            if not blocking:
                nurs.start_soon(func, *args)  # start the funcs with their args
            else:
                await func(*args)

    def addListener(self, func):  # add a listener
        logger.info(f'add listener {func}')
        self.funcs.append(func)

    def removeListener(self, func):  # remove a listener
        logger.info(f'remove listener {func}')
        self.funcs.remove(func)
