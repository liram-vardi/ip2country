from typing import Optional

from ip_analyzer.ip_storage.ip_database import IPsDataStorage, IPMetadata


# For develop and testing purpose. Do not use in Production!

class LocalIPStorage(IPsDataStorage):
    def __init__(self, csv):
        self._local_csv = csv

    def load(self):
        pass

    def get_country(self, ip: str) -> Optional[IPMetadata]:
        pass
