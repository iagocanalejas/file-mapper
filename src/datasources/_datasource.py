from abc import ABC, abstractmethod
from typing import Any

from src.core.models.metadata import Metadata
from src.core.types import Object
from src.parsers import Parser


class Datasource(ABC, Object):
    def __init__(self, parser: Parser):
        self.parser = parser


class API(Datasource, ABC):
    @abstractmethod
    def find_anime(self, keyword: str) -> Any:
        pass

    @abstractmethod
    def get_anime_details(self, anime_id: Any) -> Metadata:
        pass


class Scrapper(Datasource, ABC):
    pass
