from abc import ABC

from src.core.types import Object
from src.parsers import Parser


class Datasource(ABC, Object):
    def __init__(self, parser: Parser):
        self.parser = parser


class API(Datasource, ABC):
    pass


class Scrapper(Datasource, ABC):
    pass
