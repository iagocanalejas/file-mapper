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

    media_type: MediaType
    parser: Parser
    formatter: Formatter

    def __init_subclass__(cls, **kwargs):
        media_type = kwargs.pop('media_type')
        super().__init_subclass__(**kwargs)
        cls.media_type = media_type
        cls._registry[media_type] = cls

    def __new__(cls, media_type: MediaType, **kwargs):
        subclass = cls._registry[media_type]
        final_obj = object.__new__(subclass)
        final_obj.media_type = media_type
        final_obj.parser = Parser(media_type=media_type)
        final_obj.formatter = Formatter(media_type=media_type)

        return final_obj

    @classmethod
    def get_processor_type(cls, name: str, **kwargs) -> MediaType:
        # Try to match the parser by name
        for key, subclass in cls._registry.items():
            obj = object.__new__(subclass)
            obj.media_type = key
            if obj.matches(name, **kwargs):
                return subclass.media_type
        return MediaType.UNKNOWN

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
        item.item_name = self.formatter.new_name(self.parser, item)
        logger.info(f'{self._class}:: renamed to :: \'{item.path}\'\n')
