from enum import Enum


class DatasourceName(Enum):
    WIKIPEDIA = 'WIKIPEDIA'
    MAL = 'MAL'
    ANILIST = 'ANILIST'


class Object:
    @property
    def _class(self) -> str:
        return self.__class__.__name__
