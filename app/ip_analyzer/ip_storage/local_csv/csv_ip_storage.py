# For develop and testing purpose. Do not use in Production!
import csv
import logging
from typing import Optional

from ip_analyzer.ip_storage.ip_database import IPsDataStorage, IPMetadata

UNKNOWN = "NA"
CSV_FILE = "ips_list.csv"


class LocalIPStorage(IPsDataStorage):
    def __init__(self, conf=None):
        self._local_csv = CSV_FILE
        self._storage = None

    def load(self):
        logging.info("Starting load")
        if not self._local_csv:
            logging.error("no csv file")
            raise RuntimeError("no csv file")

        with open(self._local_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            self._storage = {}
            for row in reader:
                self._storage[row["ip"]] = IPMetadata(row["ip"], row["country"],
                                                      row["city"] if row["city"] != UNKNOWN else None)

        logging.info("Ended load")

    def get_country(self, ip: str) -> Optional[IPMetadata]:
        if self._storage is None:
            logging.error("load() was not called!")
            raise RuntimeError("load() was not called!")

        if ip in self._storage:
            return self._storage[ip]

        return None
