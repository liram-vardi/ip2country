import json
import logging
from json import JSONDecodeError
from typing import Optional

from ip_analyzer.ip_storage.ip_database import IPsDataStorage
from ip_analyzer.ip_storage.local_csv.csv_ip_storage import LocalIPStorage
from ip_analyzer.ip_storage.redis_cache.ips_redis_cache import IPCacheStorage


class IPStorageFactory:
    @staticmethod
    def create_storage(storage_type: str, conf: Optional[str]) -> IPsDataStorage:
        if not storage_type:
            logging.warning("Missing DATABASE_TYPE. Creating LOCAL_TEST analyzer")
            return LocalIPStorage()

        parsed_conf = None
        if conf:
            try:
                parsed_conf = json.loads(conf)
            except JSONDecodeError:
                logging.error("DATABASE_CONF should be in JSON format: [%s]", conf)
                raise RuntimeError("DATABASE_CONF should be in JSON format")

        storage_type_upper = storage_type.upper()

        if storage_type_upper == "LOCAL_TEST":
            return LocalIPStorage(parsed_conf)
        elif storage_type_upper == "IP_CACHE":
            return IPCacheStorage(parsed_conf)

        logging.error("UnSupported type: [%s]", storage_type)
        raise RuntimeError("UnSupported type %s" % storage_type)
