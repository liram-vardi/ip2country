from abc import ABC, abstractmethod
import time
import redis


class RateLimiter(ABC):
    @abstractmethod
    def can_be_served(self, id: str) -> bool:
        pass


class IPCacheRateLimiter(RateLimiter):
    """
    This limiter is based on the "Sliding Window" Alg of 3 sec.
    For instance, if we limit ip by 10 req/sec - then user will not be able to exec more than 10 req on the same
    sec OR more than 50 across 5 sec.
    """

    def __init__(self, redis_client: redis.Redis, limit_per_sec: int, window_size_sec=3):
        self._redis_client = redis_client
        self._limit_per_sec = limit_per_sec
        self._window_size = window_size_sec

    def can_be_served(self, id: str) -> bool:
        '''
        We limit the request by id. ID can be IP, user email or any other identifier.
        :param id:
        :return:
        '''
        current_time = int(time.time())  # The current time sec
        key = "%s#%s" % (id, str(current_time))
        new_count = self._redis_client.incr(key, 1)

        if new_count == 1:
            # This is the first value on this key --> set expire:
            self._redis_client.expire(key, self._window_size * 2)

        if new_count > self._limit_per_sec:
            # Hit the sec rate limit:
            return False

        total_windows_count = new_count
        for time_delta in range(1, self._window_size):
            previous_time_point = current_time - time_delta
            pre_key = "%s#%s" % (id, str(previous_time_point))
            pre_count = self._redis_client.get(pre_key)
            total_windows_count += int(pre_count) if pre_count else 0

        if total_windows_count > self._window_size * self._limit_per_sec:
            # Hit the window sec rate limit:
            return False

        return True
