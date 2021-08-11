import time

# class for all cache data


class Cache:
    def __init__(self, data):
        self.data = data
        self.status = data['status']
        self.cachedAt = data['cached_at']
        self.expiresAt = data['cached_until']

    def is_expired(self):
        return time.time() > self.expiresAt
