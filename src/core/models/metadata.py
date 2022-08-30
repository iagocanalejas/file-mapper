from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Tuple

from src import settings
from src.core.datasources.models import APIData
from src.core.types import DatasourceName
from src.core.types import Language
from src.core.utils.strings import generic_clean


@dataclass
class Metadata:
    title: str
    title_lang: Language

    @property
    def media_name(self, *args, **kwargs) -> str:
        return self.title


@dataclass
class AnimeMetadata(Metadata):
    datasource_data: Dict[DatasourceName, APIData] | Tuple[DatasourceName, APIData]
    season_name: Optional[str] = None
    episode_name: Optional[str] = None

    @property
    def alternative_titles(self) -> Dict[str, str]:
        if type(self.datasource_data) is tuple:
            return self.datasource_data[1].alternative_titles

        keys = set().union(*(d.alternative_titles.keys() for d in self.datasource_data.values()))
        sorted_datasource_keys = sorted(
            (k for k in settings.DATASOURCE_WEIGHT.keys()),
            key=lambda e: settings.DATASOURCE_WEIGHT[e],
            reverse=True
        )
        sorted_data = [self.datasource_data.get(k) for k in sorted_datasource_keys if self.datasource_data.get(k)]
        return {k: next((d.alternative_titles.get(k) for d in sorted_data), '') for k in keys}

    def datasource_data(self, name: DatasourceName) -> Optional[APIData]:
        if type(self.datasource_data) is dict:
            return self.datasource_data.get(name, None)
        return self.datasource_data[1] if self.datasource_data[0] == name else None

    def media_name(self, lang: Language) -> Optional[str]:
        if lang != self.title_lang and lang.value in self.alternative_titles:
            return generic_clean(self.alternative_titles[lang.value])
        return generic_clean(self.title)


def as_anime(m: Metadata) -> AnimeMetadata:
    assert isinstance(m, AnimeMetadata)
    return m
