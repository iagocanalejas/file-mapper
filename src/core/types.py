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


class SupportedSubs(Enum):
    ASS = 'ass'


class MediaType(Enum):
    UNKNOWN = 0
    ANIME = 1
    FILM = 2


class PathType(Enum):
    SHOW = 0
    SEASON = 1
    EPISODE = 2
    SUBS = 3
    OVA = 4


class Object:
    @property
    def _class(self) -> str:
        return self.__class__.__name__
