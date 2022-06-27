import logging

import redis


def create_redis_client(host, password, port, db, with_ssl):
    try:
        client = redis.StrictRedis(host=host,
                                   password=password, port=port, db=db,
                                   ssl=with_ssl)
        client.ping()
    except Exception as ex:
        logging.error("Failed to connect to Redis server at: [%s]:[%s]...", )
        raise Exception

    return client
