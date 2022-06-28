from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from src.core.models.metadata import Metadata
from src.core.types import Object, DatasourceName
from src.parsers import Parser


class Datasource(ABC, Object):
    DATASOURCE: DatasourceName

    def __init__(self, parser: Parser):
        self.parser = parser


K = TypeVar("K")
M = TypeVar("M", bound=Metadata)


class API(Datasource, ABC, Generic[K, M]):
    @abstractmethod
    def find_anime(self, keyword: str) -> K:
        pass

    @abstractmethod
    def get_anime_details(self, anime_id: K) -> M:
        pass


class Scrapper(Datasource, ABC):
    pass
