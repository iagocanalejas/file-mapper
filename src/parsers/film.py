import logging
import re

from src.core import MediaType
from src.parsers._parser import Parser
from src.utils.strings import generic_clean, apply_clean

logger = logging.getLogger()


class FilmParser(Parser, media_type=MediaType.FILM):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.FILM, **kwargs)
        return cls._instance

    @staticmethod
    def media_name(word) -> str:
        raise NotImplementedError

    @staticmethod
    def season(word) -> int:
        raise NotImplementedError

    @staticmethod
    def episode(word) -> int:
        raise NotImplementedError

    @apply_clean(clean_functions=[generic_clean])
    def matches(self, name: str, **kwargs) -> bool:
        """
       Checks if the stream is a film
       """
        return self.__matches(name)

    def __matches(self, name: str) -> bool:
        try:
            re.search(
                r'(.*)(([1-2])([890])(\d{2}))(?!p)',
                name,
                re.IGNORECASE
            ).group(0)

            logger.debug(f'{self._class_name}: \'{name}\' matches')
            return True
        except AttributeError:
            return False
