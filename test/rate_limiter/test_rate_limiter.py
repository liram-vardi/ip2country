import time
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from app.ip_analyzer.rate_limiter.limiter import IPCacheRateLimiter


class MockRedis:
    def __init__(self):
        self.storage = {}
        self.keys_ttl = {}

    def get(self, key):
        # Check if we have this key:
        value = self.storage.get(key)
        key_ttl = self.keys_ttl.get(key)

        if not key_ttl:
            return value

        current_time = int(time.time())
        if key_ttl["ttl"] + key_ttl["set_at"] <= current_time:
            # The key is expired!
            return None

        return value

    def expire(self, key, ttl):
        current_time = int(time.time())
        self.keys_ttl[key] = {
            "ttl": ttl,
            "set_at": current_time
        }

    def incr(self, key, count: int):
        if key not in self.storage:
            self.storage[key] = count
            return count

        self.storage[key] += count
        return self.storage[key]


mock_time = Mock()


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.mock_redis = MockRedis()
        self.limiter = IPCacheRateLimiter(self.mock_redis, 3, 2)
        mock_time.return_value = time.mktime(datetime(2020, 1, 1, 1, 1, 1).timetuple())

    @patch('time.time', mock_time)
    def test_simple_rate_limit_case(self):
        test_ip = '1.1.1.1'
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        self.assertEqual(self.limiter.can_be_served(test_ip), True)

        # Rate limit!
        self.assertEqual(self.limiter.can_be_served(test_ip), False)

        # Check the storage state:
        self.assertDictEqual(self.mock_redis.storage, {'1.1.1.1#1577833261': 4})
        self.assertDictEqual(self.mock_redis.keys_ttl, {'1.1.1.1#1577833261': {'set_at': 1577833261, 'ttl': 4}})

    @patch('time.time', mock_time)
    def test_two_clients_rate_limit_case(self):
        test_ip = '1.1.1.1'
        second_ip = '1.1.1.2'
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        self.assertEqual(self.limiter.can_be_served(second_ip), True)
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        self.assertEqual(self.limiter.can_be_served(test_ip), True)

        # Rate limit!
        self.assertEqual(self.limiter.can_be_served(test_ip), False)
        # Second ip should not get rate limit:
        self.assertEqual(self.limiter.can_be_served(second_ip), True)

        # Check the storage state:
        self.assertDictEqual(self.mock_redis.storage, {'1.1.1.1#1577833261': 4, '1.1.1.2#1577833261': 2})
        self.assertDictEqual(self.mock_redis.keys_ttl, {'1.1.1.1#1577833261': {'set_at': 1577833261, 'ttl': 4},
                                                        '1.1.1.2#1577833261': {'set_at': 1577833261, 'ttl': 4}})

    @patch('time.time', mock_time)
    def test_rate_limit_done_case(self):
        test_ip = '1.1.1.1'
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        self.assertEqual(self.limiter.can_be_served(test_ip), True)

        # Rate limit!
        self.assertEqual(self.limiter.can_be_served(test_ip), False)

        # move 3 sec forward  - limiting should be over now!
        mock_time.return_value = time.mktime(datetime(2020, 1, 1, 1, 1, 4).timetuple())
        self.assertEqual(self.limiter.can_be_served(test_ip), True)

        # Check the storage state:
        self.assertDictEqual(self.mock_redis.storage, {'1.1.1.1#1577833261': 4, '1.1.1.1#1577833264': 1})
        self.assertDictEqual(self.mock_redis.keys_ttl, {'1.1.1.1#1577833261': {'set_at': 1577833261, 'ttl': 4},
                                                        '1.1.1.1#1577833264': {'set_at': 1577833264, 'ttl': 4}})

    @patch('time.time', mock_time)
    def test_sliding_window_alg(self):
        test_ip = '1.1.1.1'
        # req 1 + 2 on sec 1
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        self.assertEqual(self.limiter.can_be_served(test_ip), True)

        # Move one sec forward:
        # req 3 on sec 2
        mock_time.return_value = time.mktime(datetime(2020, 1, 1, 1, 1, 2).timetuple())
        self.assertEqual(self.limiter.can_be_served(test_ip), True)
        # req 4 on sec 2 - should get rate limit
        self.assertEqual(self.limiter.can_be_served(test_ip), False)

        # Move one sec forward - The window should include now only 2 req
        mock_time.return_value = time.mktime(datetime(2020, 1, 1, 1, 1, 3).timetuple())
        self.assertEqual(self.limiter.can_be_served(test_ip), True)

        # Check the storage state:
        self.assertDictEqual(self.mock_redis.storage,
                             {'1.1.1.1#1577833261': 2, '1.1.1.1#1577833262': 2, '1.1.1.1#1577833263': 1})
        self.assertDictEqual(self.mock_redis.keys_ttl, {'1.1.1.1#1577833261': {'set_at': 1577833261, 'ttl': 4},
                                                        '1.1.1.1#1577833262': {'set_at': 1577833262, 'ttl': 4},
                                                        '1.1.1.1#1577833263': {'set_at': 1577833263, 'ttl': 4}})


if __name__ == '__main__':
    unittest.main()
