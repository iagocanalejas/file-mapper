from enum import Enum


class DatasourceName(Enum):
    WIKIPEDIA = 'WIKIPEDIA'
    MAL = 'MAL'
    ANILIST = 'ANILIST'
    IMDB = 'IMDB'
    IMDB_SCRAPPER = 'IMDB_SCRAPPER'


class Language(Enum):
    EN = 'en'
    JA = 'ja'


class Object:
    @property
    def _class(self) -> str:
        return self.__class__.__name__
