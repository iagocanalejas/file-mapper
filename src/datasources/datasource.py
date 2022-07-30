import logging
import re
from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import List
from typing import Optional
from typing import Protocol
from typing import TypeVar

from src.core.models import Episode
from src.core.models import Season
from src.core.models import Show
from src.core.models.metadata import AnimeMetadata
from src.core.models.metadata import Metadata
from src.core.types import DatasourceName
from src.core.types import Language
from src.core.types import Object
from src.datasources.models import APIData
from src.utils.strings import closest_result

logger = logging.getLogger()


class Datasource(ABC, Object):
    DATASOURCE: DatasourceName


class AnimeDatasource(Protocol):
    @abstractmethod
    def fill_show_names(self, show: Show) -> Show:
        raise NotImplemented

    @abstractmethod
    def fill_season_names(self, season: Season) -> Season:
        raise NotImplemented

    @abstractmethod
    def fill_episode_name(self, episode: Episode) -> Episode:
        raise NotImplemented


M = TypeVar('M', bound=Metadata)


class API(Datasource, ABC, Generic[M]):
    @abstractmethod
    def search_anime(self, keyword: str, lang: Language, season: int, season_name: str) -> M:
        pass


class AnimeAPI(API[Optional[AnimeMetadata]], ABC):
    @abstractmethod
    def search_anime(self, keyword: str, lang: Language, season: int, season_name: str) -> Optional[AnimeMetadata]:
        pass

    def _best_match(
            self, keyword: str, lang: Language, options: List[APIData], season: int, season_name: str
    ) -> APIData:
        valid_results = [o for o in options if self.__match_season(o.title(lang), season, season_name)]
        if not valid_results:  # We don't want to discard all the results, just trust levenshtein
            valid_results = options
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
