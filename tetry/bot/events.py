import logging

logger = logging.getLogger(__name__)


class Event:
    def __init__(self, name=None, triggerOnce=False, errorEvent=True):
        self.name = name  # only used for debbuging
        self.funcs = []
        if errorEvent:
            # event triggered when there is an error
            self.errorEvent = self.__class__(
                name=f'{name}Error', errorEvent=False)
        else:
            self.errorEvent = None
        self.triggerOnce = triggerOnce
        if self.triggerOnce:
            self.triggered = False

    async def spawner(self, nurs, func, *args):
        try:
            await func(*args)
        except BaseException as e:
            logger.info(f'event {self.name} raised {e}')
            if self.errorEvent:
                await self.errorEvent.trigger(nurs, e)
            else:
                raise e  # if there is no error event, raise the error

    # trigger event with args, runs using a nursery supplied from the run func
    async def trigger(self, nurs, *args, blocking=False):
        if self.triggerOnce and self.triggered:  # check if we can be triggered more than once
            return
        logger.info(f'trigger {self.name} with {args}')
        for func in self.funcs:
            if not blocking:
                # start the funcs with their args
                nurs.start_soon(self.spawner, nurs, func, *args)
            else:
                await self.spawner(nurs, func, *args)

    def addListener(self, func):  # add a listener
        logger.info(f'add listener {func}')
        self.funcs.append(func)

    def removeListener(self, func):  # remove a listener
        logger.info(f'remove listener {func}')
        self.funcs.remove(func)
