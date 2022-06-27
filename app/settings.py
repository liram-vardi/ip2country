import os

SENTRY_DSN = os.environ.get('SENTRY_DSN')
ENVIRONMENT = os.environ.get('ENVIRONMENT', "local")
LISTEN_PORT = int(os.environ.get('LISTEN_PORT', "3001"))

# DATABASE_TYPE CONF
LOCAL_TEST = "LOCAL_TEST"
IP_CACHE = "IP_CACHE"
DATABASE_TYPE = os.environ.get("DATABASE_TYPE", LOCAL_TEST)
DATABASE_CONF = os.environ.get("DATABASE_CONF", "{}")

# RATE LIMITER CONF:
LIMITER_REDIS_HOST = os.environ.get("LIMITER_REDIS_HOST")
LIMITER_REDIS_PORT = int(os.environ.get("LIMITER_REDIS_PORT", "6380"))
LIMITER_REDIS_PASS = os.environ.get("LIMITER_REDIS_PASS")
LIMITER_REDIS_DB = int(os.environ.get("LIMITER_REDIS_DB", "0"))
LIMITER_REDIS_DISABLE_SSL = bool(os.environ.get("LIMITER_REDIS_DISABLE_SSL"))
LIMITER_REQ_SEC = int(os.environ.get("LIMITER_REQ_SEC", "10"))
LIMITER_WINDOW_SIZE = int(os.environ.get("LIMITER_WINDOW_SIZE", "3"))
