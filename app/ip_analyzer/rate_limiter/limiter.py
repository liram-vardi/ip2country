from abc import ABC, abstractmethod
import time
import redis


class RateLimiter(ABC):
    @abstractmethod
    def can_be_served(self, id: str) -> bool:
        pass


class IPCacheRateLimiter(RateLimiter):
    """
    This limiter is based on the "Sliding Window" Alg.
    The limiter is based on 2 params: window size (sec) and requests limit.
    The limiter enforces the limit across the last window.
    For instance: if the limit is 10 req and the window size is 2 sec -
        no more than 10 req for id across the last 2 sec window is allowed...
    """

    def __init__(self, redis_client: redis.Redis, limit: int, window_size_sec=3):
        self._redis_client = redis_client
        self._limit = limit
        self._window_size = window_size_sec

    def can_be_served(self, id: str) -> bool:
        '''
        We limit the request by id. ID can be IP, user email or any other identifier.
        :param id:
        :return:
        '''
        current_time = int(time.time())  # The current time sec
        key = self._get_key(id, current_time)
        new_count = self._redis_client.incr(key, 1)

        if new_count == 1:
            # This is the first value on this key --> set expire:
            self._redis_client.expire(key, self._window_size * 2)

        if new_count > self._limit:
            # Hit the sec rate limit - no need to continue check the rest of the window counters:
            return False

        total_windows_count = new_count
        for time_delta in range(1, self._window_size):
            previous_time_point = current_time - time_delta
            pre_key = self._get_key(id, previous_time_point)
            pre_count = self._redis_client.get(pre_key)
            total_windows_count += int(pre_count) if pre_count else 0

        if total_windows_count > self._limit:
            # Hit the window sec rate limit:
            return False

        return True

    def _get_key(self, id, epoch):
        return "%s#%s" % (id, str(epoch))
