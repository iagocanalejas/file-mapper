import logging
import os.path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.core import MediaType
from src.core.exceptions import UnsupportedMediaType
from src.models.metadata import Metadata, AnimeMetadata
from src.parsers import Parser

logger = logging.getLogger()


@dataclass
class Item(ABC):
    base_path: str
    item_name: str

    def __str__(self):  # pragma: no cover
        return f'{self.full_path}'

    @property
    def _class_name(self) -> str:
        return self.__class__.__name__

    @property
    def full_path(self) -> str:
        return os.path.join(self.base_path, self.item_name)

    @abstractmethod
    def rename(self):
        pass


@dataclass
class MediaItem(Item, ABC):
    _media_type: MediaType = MediaType.UNKNOWN
    _parser: Parser = Parser
    _metadata: Optional[Metadata] = None

    def __str__(self):  # pragma: no cover
        return f'{self.media_type.name}: {super().__str__()}'

    @property
    def media_type(self) -> MediaType:
        return self._media_type

    @media_type.setter
    def media_type(self, value: MediaType):
        self._media_type = value
        self._parser = Parser(media_type=value)

    @property
    def metadata(self) -> Optional[Metadata]:
        return self._metadata

    @metadata.setter
    def metadata(self, value: Metadata):
        self._metadata = value

    @property
    def media_name(self) -> str:
        if self.metadata is None:  # pragma: no cover
            # Return a cleaned (by the parser) version of the item name
            return self._parser.media_name(self.item_name)

        if self.media_type == MediaType.ANIME:
            assert isinstance(self._metadata, AnimeMetadata)
            return self._metadata.media_name

        raise UnsupportedMediaType(f'{self}')

    @property
    @abstractmethod
    def new_name(self) -> str:
        pass

    def rename(self):
        logger.info(f'{self._class_name}:: renamed from :: \'{self.full_path}\'')
        logger.info(f'{self._class_name}:: renamed to :: \'{os.path.join(self.base_path, self.new_name)}\'\n')

        self.item_name = self.new_name
