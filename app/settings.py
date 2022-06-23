import os

SENTRY_DSN = os.environ.get('SENTRY_DSN')
ENVIRONMENT = os.environ.get('ENVIRONMENT', "local")
LISTEN_PORT = int(os.environ.get('LISTEN_PORT', "3000"))
