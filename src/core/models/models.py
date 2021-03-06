import logging
import os.path
from abc import ABC
from copy import deepcopy
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional

from src.core.models.metadata import Metadata
from src.core.types import Language
from src.core.types import Object
from src.matchers import MediaType
from src.tbuilder.models import Directory
from src.tbuilder.models import File

logger = logging.getLogger()


@dataclass
class MediaItem(ABC, Object):
    base_path: str
    item_name: str
    language: Language

    _media_type: MediaType = MediaType.UNKNOWN
    _metadata: Optional[Metadata] = None

    def __str__(self):  # pragma: no cover
        return f'{self.media_type.name}: {self.path}'

    @property
    def path(self) -> str:
        return os.path.join(self.base_path, self.item_name)

    @property
    def media_type(self) -> MediaType:
        return self._media_type

    @media_type.setter
    def media_type(self, value: MediaType):
        self._media_type = value

    @property
    def metadata(self) -> Optional[Metadata]:
        return self._metadata

    @metadata.setter
    def metadata(self, value: Metadata):
        self._metadata = value


@dataclass
class Episode(MediaItem):
    season: Optional['Season'] = None
    show: Optional['Show'] = None

    @classmethod
    def from_file(
            cls, file: File, media_type: MediaType, lang: Language, season: 'Season' = None, show: 'Show' = None
    ) -> 'Episode':  # pragma: no cover
        obj = object.__new__(cls)
        obj._media_type = media_type
        obj.language = lang
        obj.base_path = file.base_path
        obj.item_name = file.name
        obj.season = season
        obj.show = show
        return obj


@dataclass
class Season(MediaItem):
    show: Optional['Show'] = None
    episodes: List[Episode] = field(default_factory=list)

    @classmethod
    def from_directory(
            cls, directory: Directory, media_type: MediaType, lang: Language, show: 'Show' = None
    ) -> 'Season':  # pragma: no cover
        obj = object.__new__(cls)
        obj._media_type = media_type
        obj.language = lang
        obj.base_path = directory.base_path
        obj.item_name = directory.name
        obj.show = show
        obj.episodes = [
            Episode.from_file(f, media_type, lang, season=obj, show=show)
            for f in directory.childs if isinstance(f, File) and f.is_valid
        ]
        return obj

    @MediaItem.media_type.setter
    def media_type(self, value: MediaType):
        MediaItem.media_type.fset(self, value)  # Call to the super method
        for file in self.episodes:
            file.media_type = value

    @MediaItem.metadata.setter
    def metadata(self, value: Metadata):
        MediaItem.metadata.fset(self, value)  # Call to the super method
        for file in self.episodes:
            file.metadata = deepcopy(value)


@dataclass
class Show(MediaItem):
    seasons: List[Season] = field(default_factory=list)
    episodes: List[Episode] = field(default_factory=list)

    @classmethod
    def from_directory(cls, directory: Directory, media_type: MediaType, lang: Language) -> 'Show':  # pragma: no cover
        obj = object.__new__(cls)
        obj._media_type = media_type
        obj.language = lang
        obj.base_path = directory.base_path
        obj.item_name = directory.name
        obj.episodes = [
            Episode.from_file(f, media_type, lang, show=obj)
            for f in directory.childs if isinstance(f, File) and f.is_valid
        ]

        seasons: List[Season] = []
        for subdirectory in [d for d in directory.childs if isinstance(d, Directory) and d.is_valid]:
            if not subdirectory.has_only_files():
                raise ValueError(f'{obj}')
            seasons.append(Season.from_directory(subdirectory, media_type, lang, show=obj))

        obj.seasons = seasons
        return obj

    @MediaItem.media_type.setter
    def media_type(self, value: MediaType):
        MediaItem.media_type.fset(self, value)  # Call to the super method
        for season in self.seasons:
            season.media_type = value
        for file in self.episodes:
            file.media_type = value

    @MediaItem.metadata.setter
    def metadata(self, value: Metadata):
        MediaItem.metadata.fset(self, value)  # Call to the super method
        for file in self.episodes:
            file.metadata = deepcopy(value)
        for season in self.seasons:
            season.metadata = deepcopy(value)
