from abc import ABC, abstractmethod
from typing import NamedTuple, Optional


class IPMetadata(NamedTuple):
    ip: str
    country: str
    city: Optional[str]


class IPsDataStorage(ABC):
    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def get_country(self, ip: str) -> Optional[IPMetadata]:
        pass
