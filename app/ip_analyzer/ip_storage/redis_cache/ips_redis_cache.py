import json
import logging
from typing import Optional

import redis

from ip_analyzer.ip_storage.ip_database import IPsDataStorage, IPMetadata

UNKNOWN = "NA"


class IPCacheStorage(IPsDataStorage):
    def __init__(self, conf):
        self._rd_host = conf.get("host")
        self._rd_port = int(conf.get("port", "6380"))
        self._rd_pass = conf.get("password")
        self._rd_db = int(conf.get("db", "0"))

        self._rd_client = None

    def load(self):
        logging.info("Connection to redis at: [%s] ", self._rd_host)

        if not self._rd_host:
            logging.error("Missing 'host'. Check configuration")
            raise RuntimeError("Missing 'host'. Check configuration")

        if not self._rd_pass:
            logging.error("Missing 'password'. Check configuration")
            raise RuntimeError("Missing 'password'. Check configuration")

        try:
            self._rd_client = redis.StrictRedis(host=self._rd_host,
                                                password=self._rd_pass, port=self._rd_pass, db=self._rd_db, ssl=True)
        except Exception as ex:
            logging.exception("Failed to connect to Redis: [%s]", str(ex))

    def get_country(self, ip: str) -> Optional[IPMetadata]:
        if not self._rd_client:
            logging.error("load() was not called! - No Connection")
            raise RuntimeError("load() was not called! - No Connection")

        ip_data = None
        try:
            ip_data = self._rd_client.get(ip)
            if not ip_data:
                return None

            data_parsed = json.loads(ip_data)

            return IPMetadata(ip=ip, country=data_parsed["country"],
                              city=(data_parsed["city"] if data_parsed["city"] != UNKNOWN else None))
        except Exception as ex:
            logging.exception("Failed to get ip data from cache: [%s]. Error: [%s]", ip_data, str(ex))
            raise RuntimeError("Failed to get ip data from cache")
