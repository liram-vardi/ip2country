import json
import logging
from json import JSONDecodeError

from ip_analyzer.ip_storage.ip_database import IPsDataStorage
from ip_analyzer.ip_storage.local_csv.csv_ip_storage import LocalIPStorage
from ip_analyzer.ip_storage.redis_cache.ips_redis_cache import IPCacheStorage
from settings import DATABASE_CONF, DATABASE_TYPE, LOCAL_TEST, IP_CACHE


def create_storage() -> IPsDataStorage:
    parsed_conf = None
    if DATABASE_CONF:
        try:
            parsed_conf = json.loads(DATABASE_CONF)
        except JSONDecodeError:
            logging.error("DATABASE_CONF should be in JSON format: [%s]", conf)
            raise RuntimeError("DATABASE_CONF should be in JSON format")

    if DATABASE_TYPE == LOCAL_TEST:
        model = LocalIPStorage()
    elif DATABASE_TYPE == IP_CACHE:
        model = IPCacheStorage(parsed_conf)
    else:
        logging.error("UnSupported type: [%s]", DATABASE_TYPE)
        raise RuntimeError("UnSupported type %s" % DATABASE_TYPE)
    logging.info("Initting %s", DATABASE_TYPE)
    model.load()

    return model
