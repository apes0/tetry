import time

# class for all cache data


class Cache:
    '''
     Cache class for TETR.IO data.
    '''

    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.status: str = data['status']
        self.cached_at: int = data['cached_at']
        self.expires_at: int = data['cached_until']

    def is_expired(self) -> bool:
        '''
        is_expired Return True if the cache has expired.

        :return: True if the cache has expired.
        :rtype: bool
        '''
        return time.time() > self.expires_at
