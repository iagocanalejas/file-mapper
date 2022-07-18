from abc import ABC
from abc import abstractmethod

from src.core.models import MediaItem
from src.core.types import Language
from src.core.types import Object
from src.matchers import MediaType
from src.parsers import Parser


class Formatter(ABC, Object):
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

    @staticmethod
    def titlecase(word: str, **kwargs) -> str:
        return word.title()

    @abstractmethod
    def new_name(self, item: MediaItem, parser: Parser) -> str:
        pass

    @abstractmethod
    def format(self, item: MediaItem, parser: Parser, pattern: str, lang: Language = Language.EN) -> str:
        pass
