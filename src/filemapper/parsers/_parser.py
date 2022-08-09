from abc import ABC
from abc import abstractmethod
from typing import Optional

from src.core.models import MediaItem
from src.core.types import Object
from src.filemapper.matchers import MediaType
from src.utils.strings import generic_clean
from src.utils.strings import retrieve_extension


class Parser(ABC, Object):
    _registry = {}
    media_type: MediaType

    def __init_subclass__(cls, **kwargs):
        media_type = kwargs.pop('media_type')
        super().__init_subclass__(**kwargs)
        cls._registry[media_type] = cls

    def __new__(cls, *args, media_type: MediaType, **kwargs):  # pragma: no cover
        subclass = cls._registry[media_type]
        final_obj = object.__new__(subclass)
        final_obj.media_type = media_type
        return final_obj

    @abstractmethod
    def episode(self, item: MediaItem) -> int:
        pass

    @abstractmethod
    def episode_part(self, item: MediaItem) -> Optional[int]:
        """
        :return: things like .5 episodes
        """
        pass

    @abstractmethod
    def episode_name(self, item: MediaItem, use_metadata: bool = True) -> Optional[str]:
        pass

    @abstractmethod
    def season(self, item: MediaItem) -> int:
        pass

    @abstractmethod
    def season_name(self, item: MediaItem, use_metadata: bool = True) -> Optional[str]:
        pass

    @abstractmethod
    def media_title(self, item: MediaItem) -> Optional[str]:
        """
        Will try to return only the name of the media_file, without episode or season present
        :return: Seikon no Qwaser
        """
        pass

    @staticmethod
    def extension(item: MediaItem) -> Optional[str]:
        return retrieve_extension(generic_clean(item.item_name))
