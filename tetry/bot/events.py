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
    async def trigger(self, nurs, *args):
        if self.triggerOnce:  # check if we can be triggered more than once
            if self.triggered:  # return if we have been triggered more than once
                return
        logger.info(f'trigger {self.name} with {args}')
        for func in self.funcs:
            nurs.start_soon(func, *args)  # start the funcs with their args

    def addListener(self, func):  # add a listener
        logger.info(f'add listener {func}')
        self.funcs.append(func)

    def removeListener(self, func):  # remove a listener
        logger.info(f'remove listener {func}')
        self.funcs.remove(func)
