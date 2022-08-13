import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.core.formatter import Formatter
from src.core.models import MediaItem
from src.core.types import MediaType
from src.core.types import Object
from src.core.types import PathType

logger = logging.getLogger()


@dataclass
class ProcessorConfig:
    path_type: Optional[PathType] = None

    def __str__(self):
        return f"""
            path_type: {self.path_type}
        """


class Processor(ABC, Object):
    _registry = {}

    _config: ProcessorConfig
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

    def __new__(cls, media_type: MediaType, config: ProcessorConfig, **kwargs):  # pragma: no cover
        subclass = cls._registry[media_type]
        final_obj = object.__new__(subclass)
        final_obj._config = config
        final_obj._formatter = Formatter(media_type=media_type)
        final_obj._media_type = media_type

        return final_obj

    @abstractmethod
    def process(self, item: MediaItem):
        pass

    @abstractmethod
    def post_process(self, item: MediaItem):
        pass
