import logging
from abc import ABC
from abc import abstractmethod

from src.core.formatter import Formatter
from src.core.types import MediaType
from src.core.types import Object

logger = logging.getLogger()


class Processor(ABC, Object):
    _registry = {}

    _formatter: Formatter
    _media_type: MediaType

    @property
    def media_type(self) -> MediaType:
        return self._media_type

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
        final_obj._formatter = Formatter(media_type=media_type)
        final_obj._media_type = media_type

        return final_obj

    @abstractmethod
    def process(self, **kwargs):
        pass

    @abstractmethod
    def post_process(self, **kwargs):
        pass
