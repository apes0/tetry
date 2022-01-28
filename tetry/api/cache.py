import time

# class for all cache data


class Cache:
    def __init__(self, data):
        self.data = data
        self.status = data['status']
        self.cached_at = data['cached_at']
        self.expires_at = data['cached_until']

    def is_expired(self):
        return time.time() > self.expires_at
