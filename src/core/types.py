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

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class SupportedSubs(Enum):
    ASS = 'ass'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class MediaType(Enum):
    SUBS = -1
    UNKNOWN = 0
    ANIME = 1
    FILM = 2


class PathType(Enum):
    SHOW = 0
    SEASON = 1
    EPISODE = 2
    OVA = 3


class SubtitleAction(Enum):
    RENAME = 0
    MERGE = 1


class Object:
    @property
    def _class(self) -> str:
        return self.__class__.__name__
