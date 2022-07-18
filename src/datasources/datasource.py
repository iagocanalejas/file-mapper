import logging
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Generic
from typing import List
from typing import TypeVar

from src.core.models.metadata import AnimeMetadata
from src.core.models.metadata import Metadata
from src.core.types import DatasourceName
from src.core.types import Language
from src.core.types import Object
from src.parsers import Parser
from src.utils.strings import closest_result

logger = logging.getLogger()


class Datasource(ABC, Object):
    DATASOURCE: DatasourceName

    def __init__(self, parser: Parser):
        self.parser = parser


M = TypeVar('M', bound=Metadata)


class API(Datasource, ABC, Generic[M]):
    @abstractmethod
    def search_anime(self, keyword: str, lang: Language, season: int, season_name: str) -> M:
        pass


class AnimeAPI(API[AnimeMetadata], ABC):
    @abstractmethod
    def search_anime(self, keyword: str, lang: Language, season: int, season_name: str) -> AnimeMetadata:
        pass

    def _best_match(
            self, keyword: str, lang: Language, options: List['APIData'], season: int, season_name: str
    ) -> 'APIData':
        valid_results = [o for o in options if self.__match_season(o.title(lang), season, season_name)]
        closest_name = closest_result(keyword=keyword, elements=[d.title(lang) for d in valid_results])
        return [d for d in valid_results if d.title(lang) == closest_name][0]

    @staticmethod
    def __match_season(name: str, season: int, season_name: str) -> bool:
        season_re = f's(eason )?{season}'
        if season > 1:
            return season_name in name \
                   or re.search(season_re, name, re.IGNORECASE) is not None
        return re.search(season_re, name, re.IGNORECASE) is None  # simple no season check


class Scrapper(Datasource, ABC):
    pass


@dataclass
class APIData:
    id: int
    _title: str
    alternative_titles: Dict[str, str]

    def __str__(self):
        return f'{self.id} -- {self._title}'

    def __init__(self, d: Dict):
        self.id = d['id']

    def title(self, lang: Language = Language.JA):
        if lang == Language.JA:
            return self._title
        return self.alternative_titles[lang.value] if self.alternative_titles[lang.value] else self._title
