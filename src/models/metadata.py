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
    mal_id: int
    media_type: str
    alternative_titles: Dict[str, str]
    episode_name: Optional[str] = None

    @property
    def media_name(self) -> str:
        name = self.title
        if self.alternative_titles and self.alternative_titles['en']:
            name = self.alternative_titles['en']
        return generic_clean(name)
