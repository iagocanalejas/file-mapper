import logging
from abc import ABC, abstractmethod

from src.core import MediaType
from src.models import Episode, Season, Show
from src.parsers import Parser

logger = logging.getLogger()


class Processor(ABC):
    _registry = {}

    media_type: MediaType
    parser: Parser

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, media_type: MediaType, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[media_type] = cls

    def __new__(cls, parser: Parser, **kwargs):
        assert parser.media_type in cls._registry.keys()

        subclass = cls._registry[parser.media_type]
        final_obj = object.__new__(subclass)

        final_obj.paser = parser
        final_obj.media_type = parser.media_type

        return final_obj

    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def process_episode(self, episode: Episode):
        episode.media_type = self.media_type
        logger.info(f'{self.name}:: processing episode :: {episode}')

    @abstractmethod
    def process_season(self, season: Season):
        season.media_type = self.media_type
        logger.info(f'{self.name}:: processing season :: {season}')

    @abstractmethod
    def process_show(self, show: Show):
        show.media_type = self.media_type
        logger.info(f'{self.name}:: processing show :: {show}')


