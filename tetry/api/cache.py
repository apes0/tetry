import time

# class for all cache data


class Cache:
    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.status: str = data['status']
        self.cached_at: int = data['cached_at']
        self.expires_at: int = data['cached_until']

    def is_expired(self) -> bool:
        return time.time() > self.expires_at
