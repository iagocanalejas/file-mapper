import logging
import re
from abc import ABC
from abc import abstractmethod
from enum import Enum

from src.core.types import Object
from src.utils.strings import apply_clean
from src.utils.strings import generic_clean

logger = logging.getLogger()


class MediaType(Enum):
    UNKNOWN = 0
    ANIME = 1
    FILM = 2


class TypeMatcher(ABC, Object):
    media_type: MediaType

    @abstractmethod
    def matches(self, name: str) -> bool:
        pass


class AnimeTypeMatcher(TypeMatcher):
    media_type: MediaType = MediaType.ANIME

    @apply_clean(clean_functions=[generic_clean])
    def matches(self, name: str) -> bool:
        """
        Checks if the stream is an anime show
        """
        return self.__full_match(name) or self.__partial_match(name)

    def __full_match(self, name: str) -> bool:
        try:
            re.search(
                r'\[(\w+-?)*](\s\w+)*\s(.?\s)?(\d{0,3}|E\w{0,6}.?\d{0,3})\s?\(?\[?(\d{3,4}p|.*)\)?]?',
                name,
                re.IGNORECASE
            ).group(0)

            logger.debug(f'{self._class}: \'{name}\' matches full regex')
            return True
        except AttributeError:
            return False

    def __partial_match(self, name: str) -> bool:
        try:
            re.search(r'(^\[(\w+(\s?|-|.?))+])', name, re.IGNORECASE).group(0)
            re.search(r'-(.?)\d{1,3}|(x|E(pisode)?)(\s|\.|-)?\d{1,3}', name, re.IGNORECASE).group(0)

            logger.debug(f'{self._class}: \'{name}\' matches partial regex')
            return True
        except AttributeError:
            return False


class FilmTypeMatcher(TypeMatcher):
    media_type: MediaType = MediaType.FILM

    @apply_clean(clean_functions=[generic_clean])
    def matches(self, name: str) -> bool:
        """
        Checks if the stream is a film
        """
        return self.__matches(name)

    def __matches(self, name: str) -> bool:
        try:
            # (?:19|20|21)\d{2}(?!p): matches a year between 1900 and 2199 and avoid matching the quality XXXXp
            re.search(
                r'(.*)(?:19|20|21)\d{2}(?!p)',
                name,
                re.IGNORECASE
            ).group(0)

            logger.debug(f'{self._class}: \'{name}\' matches')
            return True
        except AttributeError:
            return False
