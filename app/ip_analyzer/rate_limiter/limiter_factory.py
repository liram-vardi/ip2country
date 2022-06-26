import logging

import redis

from ip_analyzer.rate_limiter.limiter import IPCacheRateLimiter
from settings import LIMITER_REDIS_HOST, LIMITER_REDIS_PASS, LIMITER_REDIS_PORT, LIMITER_REDIS_DB, LIMITER_REQ_SEC, \
    LIMITER_WINDOW_SIZE, LIMITER_REDIS_DISABLE_SSL


def create_rate_limiter() -> IPCacheRateLimiter:
    if not LIMITER_REDIS_HOST:
        logging.error("Missing REDIS_HOST env!")
        raise RuntimeError("Missing REDIS_HOST env!")

    if not LIMITER_REDIS_PASS:
        logging.error("Missing REDIS_PASS env!")
        raise RuntimeError("Missing REDIS_PASS env!")

    logging.info("Starting Redis client on [%s:%s] with%s ssl...", LIMITER_REDIS_HOST, LIMITER_REDIS_PORT,
                 "out" if LIMITER_REDIS_DISABLE_SSL else "")

    redis_client = redis.StrictRedis(host=LIMITER_REDIS_HOST,
                                     password=LIMITER_REDIS_PASS,
                                     port=LIMITER_REDIS_PORT,
                                     db=LIMITER_REDIS_DB,
                                     ssl=False if LIMITER_REDIS_DISABLE_SSL else True)

    return IPCacheRateLimiter(redis_client, LIMITER_REQ_SEC, LIMITER_WINDOW_SIZE)
