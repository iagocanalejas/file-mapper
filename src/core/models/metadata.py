from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

from src.core.types import DatasourceName
from src.core.types import Language
from src.utils.strings import generic_clean


@dataclass
class Metadata:
    title: str

    @property
    def media_name(self, *args, **kwargs) -> str:
        return self.title


@dataclass
class AnimeMetadata(Metadata):
    datasource_id: List[int] | int
    datasource: List[DatasourceName] | DatasourceName
    alternative_titles: Dict[str, str]
    season_name: Optional[str] = None
    episode_name: Optional[str] = None

    def media_name(self, lang: Language) -> str:
        if lang == Language.JA:
            return generic_clean(self.title)
        name = self.title
        if self.alternative_titles and self.alternative_titles[lang.value]:
            name = self.alternative_titles[lang.value]
        return generic_clean(name)
