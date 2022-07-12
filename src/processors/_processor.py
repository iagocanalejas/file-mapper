import logging
from abc import ABC, abstractmethod

from src.core.models import Episode, Season, Show, MediaItem
from src.core.types import Object
from src.formatter import Formatter
from src.parsers import Parser
from src.matchers import MediaType

logger = logging.getLogger()


class Processor(ABC, Object):
    _registry = {}

    _media_type: MediaType
    _parser: Parser
    _formatter: Formatter

    @property
    def media_type(self) -> MediaType:
        return self._media_type

    @property
    def parser(self) -> Parser:
        return self._parser

    @property
    def formatter(self) -> Formatter:
        return self._formatter

    def __init_subclass__(cls, **kwargs):
        media_type = kwargs.pop('media_type')
        super().__init_subclass__(**kwargs)
        cls._media_type = media_type
        cls._registry[media_type] = cls

    def __new__(cls, media_type: MediaType, **kwargs):  # pragma: no cover
        subclass = cls._registry[media_type]
        final_obj = object.__new__(subclass)
        final_obj._media_type = media_type
        final_obj._parser = Parser(media_type=media_type)
        final_obj._formatter = Formatter(media_type=media_type)

        return final_obj

    @abstractmethod
    def process_episode(self, episode: Episode):
        episode.media_type = self.media_type
        logger.info(f'{self._class}:: processing episode :: {episode}')

    @abstractmethod
    def process_season(self, season: Season):
        season.media_type = self.media_type
        logger.info(f'{self._class}:: processing season :: {season}')

    @abstractmethod
    def process_show(self, show: Show):
        show.media_type = self.media_type
        logger.info(f'{self._class}:: processing show :: {show}')

    @abstractmethod
    def rename(self, item: MediaItem):
        logger.info(f'{self._class}:: renamed from :: \'{item.path}\'')
        item.item_name = self.formatter.new_name(item, self.parser)
        logger.info(f'{self._class}:: renamed to :: \'{item.path}\'\n')
