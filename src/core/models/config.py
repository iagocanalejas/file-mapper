from typing import Dict
from typing import Optional

from src.core.types import DatasourceName
from src.core.types import Language
from src.core.types import MediaType


class GlobalConfig:
    media_type: Optional[MediaType] = None
    language: Optional[Language] = None
    datasource: Optional[Dict[DatasourceName, str]] = {}

    # Ensure only one GlobalConfig exists
    __instance: Optional['GlobalConfig'] = None

    def __new__(cls, *args, **kwargs) -> 'GlobalConfig':  # pragma: no cover
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __str__(self):
        return f"""\n\tmedia_type: {self.media_type}\n\tlanguage: {self.language}\n\tdatasource: {self.datasource}"""

    @property
    def wikipedia_url(self) -> Optional[str]:
        return self.datasource[DatasourceName.WIKIPEDIA] if DatasourceName.WIKIPEDIA in self.datasource else None

    @wikipedia_url.setter
    def wikipedia_url(self, value: str):
        self.datasource[DatasourceName.WIKIPEDIA] = value

    @property
    def mal_url(self) -> Optional[str]:
        return self.datasource[DatasourceName.MAL] if DatasourceName.MAL in self.datasource else None

    @mal_url.setter
    def mal_url(self, value: str):
        self.datasource[DatasourceName.MAL] = value
