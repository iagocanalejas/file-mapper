from dataclasses import dataclass
from typing import Optional, Dict

from src.utils.strings import generic_clean


@dataclass
class Metadata:
    title: str

    @property
    def media_name(self) -> str:
        return self.title


@dataclass
class AnimeMetadata(Metadata):
    datasource_id: int
    media_type: str
    alternative_titles: Dict[str, str]
    season_name: Optional[str] = None
    episode_name: Optional[str] = None

    seasoned: bool = False  # Whether the 'media_name' will contain the season

    def media_name(self, lang: str = 'en') -> str:
        if lang == 'ja':
            return generic_clean(self.title)
        name = self.title
        if self.alternative_titles and self.alternative_titles[lang]:
            name = self.alternative_titles[lang]
        return generic_clean(name)
