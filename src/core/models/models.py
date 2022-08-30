import logging
import os.path
from abc import ABC
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import TypeVar

from polyglot.text import Text

from src import settings
from src.core.models.metadata import Metadata
from src.core.types import Language
from src.core.types import MediaType
from src.core.types import Object
from src.core.utils.strings import generic_clean
from src.core.utils.strings import remove_brackets
from src.core.utils.strings import retrieve_extension
from src.filemapper.tbuilder.models import Directory
from src.filemapper.tbuilder.models import File

logger = logging.getLogger()

T = TypeVar('T', bound='MediaItem')


@dataclass
class ParsedInfo:
    episode: Optional[int]
    episode_part: Optional[int]
    season: Optional[int]
    season_name: Optional[str]
    media_title: str
    extension: Optional[str]

    @classmethod
    def parse(cls, item: T, parser=None) -> T:
        """
        Parse the input #MediaItem to extract all the data found in the name.
        :return: #MediaItem with filled `parsed` field.
        """
        from src.core.parsers import Parser

        parser = parser if parser is not None else Parser(media_type=item.media_type)
        assert isinstance(parser, Parser)

        media_title = parser.media_title(item)
        episode = episode_part = season = season_name = extension = None
        match item:
            case Episode() | SubsFile():
                episode = parser.episode(item)
                episode_part = parser.episode_part(item)
                season = parser.season(item)
                season_name = parser.season_name(item)
                extension = parser.extension(item)
            case Season():
                assert isinstance(item, Season)
                [cls.parse(e, parser=parser) for e in item.episodes]

                season = parser.season(item)
                season_name = parser.season_name(item)
            case Show():
                assert isinstance(item, Show)
                [cls.parse(s, parser=parser) for s in item.seasons]

        item.parsed = ParsedInfo(
            episode=episode,
            episode_part=episode_part,
            season=season,
            season_name=season_name,
            media_title=media_title,
            extension=extension,
        )
        return item


@dataclass
class MediaItem(ABC, Object):
    base_path: str
    item_name: str
    parsed: Optional[ParsedInfo]

    _language: Optional[Language] = None
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

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value

    @abstractmethod
    def flatten(self) -> List['MediaItem']:
        """
        Retrieve all the childs for the current #MediaItem and returns them as a list.
        :return: List of items being 'self' the first one.
        """
        pass

    @abstractmethod
    def update(self: T, name: str, value) -> T:
        """
        Updates the object #name field with the provided #value.
        :return: #MediaItem with the updated field or no changes
        """
        pass

    @abstractmethod
    def rename(self, new_name):
        """
        Renames the #MediaItem with the provided #new_name.
        """
        pass


@dataclass
class Episode(MediaItem):
    season: Optional['Season'] = None
    show: Optional['Show'] = None

    @classmethod
    def from_file(
            cls, file: File, season: 'Season' = None, show: 'Show' = None
    ) -> 'Episode':  # pragma: no cover
        obj = object.__new__(cls)
        obj.base_path = file.base_path
        obj.item_name = file.name
        obj.season = season
        obj.show = show
        return obj

    def update(self, name: str, value) -> 'Episode':
        match name:
            case 'base_path':
                self.base_path = value
            case _:
                setattr(self.metadata, name, value)
        return self

    def flatten(self) -> List[MediaItem]:
        return [self]

    def rename(self, new_name):
        logger.debug(f'{self._class}:: {self.path} :: {new_name}')
        if not settings.DEBUG:
            os.renames(self.path, os.path.join(self.base_path, new_name))
        self.item_name = new_name


@dataclass
class Season(MediaItem):
    show: Optional['Show'] = None
    episodes: List[Episode] = field(default_factory=list)

    @classmethod
    def from_directory(
            cls, directory: Directory, show: 'Show' = None
    ) -> 'Season':  # pragma: no cover
        obj = object.__new__(cls)
        obj.base_path = directory.base_path
        obj.item_name = directory.name
        obj.show = show
        obj.episodes = [
            Episode.from_file(f, season=obj, show=show) for f in directory.childs if isinstance(f, File) and f.is_valid
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

    def update(self, name: str, value) -> 'Season':
        match name:
            case 'base_path':
                self.base_path = value
                [e.update(name, self.path) for e in self.episodes]
            case _:
                setattr(self.metadata, name, value)
                [e.update(name, value) for e in self.episodes]
        return self

    def flatten(self) -> List[MediaItem]:
        items = [self]
        for episode in self.episodes:
            items.extend(episode.flatten())
        return items

    def rename(self, new_name):
        if not settings.DEBUG:
            new_path = os.path.join(self.base_path, new_name)
            os.renames(self.path, new_path)
            [e.update('base_path', new_path) for e in self.episodes]
        self.item_name = new_name


@dataclass
class Show(MediaItem):
    seasons: List[Season] = field(default_factory=list)

    @classmethod
    def from_directory(cls, directory: Directory) -> 'Show':  # pragma: no cover
        obj = object.__new__(cls)
        obj.base_path = directory.base_path
        obj.item_name = directory.name

        seasons: List[Season] = []
        for subdirectory in [d for d in directory.childs if isinstance(d, Directory) and d.is_valid]:
            if not subdirectory.has_only_files():
                raise ValueError(f'{obj}')
            seasons.append(Season.from_directory(subdirectory, show=obj))

        obj.seasons = seasons
        return obj

    @MediaItem.media_type.setter
    def media_type(self, value: MediaType):
        MediaItem.media_type.fset(self, value)  # Call to the super method
        for season in self.seasons:
            season.media_type = value

    @MediaItem.metadata.setter
    def metadata(self, value: Metadata):
        MediaItem.metadata.fset(self, value)  # Call to the super method
        for season in self.seasons:
            season.metadata = deepcopy(value)

    def update(self, name: str, value) -> 'Show':
        match name:
            case 'base_path':
                self.base_path = value
                [s.update(name, self.path) for s in self.seasons]
            case _:
                setattr(self.metadata, name, value)
                [s.update(name, value) for s in self.seasons]
        return self

    def flatten(self) -> List[MediaItem]:
        items = [self]
        for season in self.seasons:
            items.extend(season.flatten())
        return items

    def rename(self, new_name):
        if not settings.DEBUG:
            new_path = os.path.join(self.base_path, new_name)
            os.renames(self.path, new_path)
            [s.update('base_path', new_path) for s in self.seasons]
        self.item_name = new_name


@dataclass
class SubsFile(MediaItem):
    parent: Optional[Episode] = None

    _media_type = MediaType.SUBS

    def __str__(self):  # pragma: no cover
        return f'{self.media_type.name}: subs : {self.path}'

    @property
    def media_type(self) -> MediaType:
        return self._media_type

    @property
    def metadata(self) -> Optional[Metadata]:
        return self.parent.metadata if self.parent else None

    @property
    def language(self) -> Language:
        """
        Parse and localize the subtitles string to find the language.
        :return: The #Language of the file content.
        """
        if self._language is None:
            match retrieve_extension(generic_clean(self.item_name)):
                case 'ass':
                    self._language = self.__ass_language()
        return self._language

    def update(self, name: str, value) -> 'SubsFile':
        match name:
            case 'parent':
                self.parent = value
            case _:
                pass
        return self

    def flatten(self) -> List['MediaItem']:
        return [self]

    def rename(self, new_name):
        if not settings.DEBUG:
            subs_folder = os.path.join(self.parent.base_path, os.path.basename(self.base_path))
            os.rename(os.path.join(subs_folder, self.item_name), os.path.join(subs_folder, new_name))
        self.item_name = new_name

    def __ass_language(self) -> Language:
        with open(self.path) as subs_file:
            text = subs_file.read()
            assert '[Events]' in text

            events = text.split('[Events]')[1].split('\n')
            events = [remove_brackets(e.split(',')[-1]).strip() for e in events if ',' in e]
            languages = [Text(e).language.code for e in events]
            language = max(languages, key=languages.count)

            if language and language.upper() in Language.__members__.values():
                return Language[language.upper()]
        logger.error(f'{self}:: no language match')

    ########################
    #       Forbidden      #
    ########################

    @language.setter
    def language(self, value):
        raise NotImplementedError

    @metadata.setter
    def metadata(self, value: Metadata):
        raise NotImplementedError

    @media_type.setter
    def media_type(self, value: MediaType):
        raise NotImplementedError
