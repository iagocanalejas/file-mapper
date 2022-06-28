from dataclasses import dataclass
from typing import Optional, Dict, List

from src.core.types import DatasourceName
from src.utils.strings import generic_clean


@dataclass
class Metadata:
    title: str

    @property
    def media_name(self) -> str:
        return self.title


@dataclass
class AnimeMetadata(Metadata):
    datasource_id: List[int] | int
    datasource: List[DatasourceName] | DatasourceName
    alternative_titles: Dict[str, str]
    season_name: Optional[str] = None
    episode_name: Optional[str] = None

    def media_name(self, lang: str = 'en') -> str:
        if lang == 'ja':
            return generic_clean(self.title)
        name = self.title
        if self.alternative_titles and self.alternative_titles[lang]:
            name = self.alternative_titles[lang]
        return generic_clean(name)
