import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Dict, List

from polyglot.text import Text

from src.core.models.metadata import Metadata, AnimeMetadata
from src.core.types import Object, DatasourceName
from src.parsers import Parser
from src.utils.strings import closest_result

logger = logging.getLogger()


class Datasource(ABC, Object):
    DATASOURCE: DatasourceName

    def __init__(self, parser: Parser):
        self.parser = parser


M = TypeVar("M", bound=Metadata)


class API(Datasource, ABC, Generic[M]):
    __ACCEPTED_LANGUAGES = ['en', 'ja']
    __DEFAULT_LANGUAGE = 'ja'

    @abstractmethod
    def search_anime(self, keyword: str, season: int, season_name: str) -> M:
        pass

    def _get_lang(self, keyword: str) -> str:
        lang = Text(keyword).language.code
        lang = lang if lang in self.__ACCEPTED_LANGUAGES else self.__DEFAULT_LANGUAGE
        logger.info(f'{self._class}:: using language :: {lang}')
        return lang


class AnimeAPI(API[AnimeMetadata], ABC):
    @abstractmethod
    def search_anime(self, keyword: str, season: int, season_name: str) -> AnimeMetadata:
        pass

    def _best_match(self, keyword: str, options: List['APIData'], season: int, season_name: str) -> 'APIData':
        lang: str = self._get_lang(keyword)

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

    def title(self, lang: str = 'ja'):
        if lang == 'ja':
            return self._title
        return self.alternative_titles[lang] if self.alternative_titles[lang] else self._title
