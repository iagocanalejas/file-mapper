import re
from abc import ABC, abstractmethod
from typing import Optional

from src.core import MediaType
from src.utils.string import clean_strings, RomanNumbers


class Parser(ABC):
    _registry = {}
    media_type: MediaType

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, media_type: MediaType, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[media_type] = cls

    def __new__(cls, name: str = None, media_type: MediaType = None, **kwargs):
        assert name is not None or media_type is not None

        if media_type is not None:
            # Returns the matching class
            subclass = cls._registry[media_type]
            final_obj = object.__new__(subclass)
            final_obj.media_type = media_type
            return final_obj

        final_obj = None
        for key, subclass in cls._registry.items():
            if key == MediaType.UNKNOWN:
                continue

            # Try to match the parser by name
            obj = object.__new__(subclass)
            obj.media_type = key
            if obj.matches(name, **kwargs):
                final_obj = obj
                break

        if final_obj is None:
            subclass = cls._registry[MediaType.UNKNOWN]
            final_obj = object.__new__(subclass)
            final_obj.media_type = MediaType.UNKNOWN

        return final_obj

    @staticmethod
    def titlecase(word: str) -> str:
        return word.title()

    @abstractmethod
    def matches(self, name: str, **kwargs) -> bool:
        pass

    @property
    def _class_name(self):
        return self.__class__.__name__

    @staticmethod
    @clean_strings
    def season(word: str) -> int:
        match = re.search(r'Season \d+', word, re.IGNORECASE)
        if match is not None:
            # Matches Season 1
            return int(match.group(0).replace('Season ', ''))

        match = re.search(r'S\d+E\d+', word, re.IGNORECASE)
        if match is not None:
            # Matches S1E1
            return int(re.findall(r'\d+', match.group(0))[0])

        match = re.search(r'S\d -', word, re.IGNORECASE)
        if match is not None:
            # Matches S1 -
            return int(re.findall(r'\d+', match.group(0))[0])

        match = re.search(r' (IX|IV|V?I{0,3})( |$)', word)
        if match is not None:
            # Matches roman numbers
            return RomanNumbers[match.group(0).strip()].value

        return 1

    @staticmethod
    @clean_strings
    def season_text(word: str) -> Optional[str]:
        match = re.search(r'Season \d+', word, re.IGNORECASE)
        if match is not None:
            # Matches Season 1
            return match.group(0).replace('Season ', '')

        match = re.search(r'S\d+E\d+', word, re.IGNORECASE)
        if match is not None:
            # Matches S1E1
            return re.findall(r'\d+', match.group(0))[0]

        match = re.search(r'S\d -', word, re.IGNORECASE)
        if match is not None:
            # Matches S1 -
            return re.findall(r'\d+', match.group(0))[0]

        match = re.search(r' (IX|IV|V?I{0,3})( |$)', word)
        if match is not None:
            # Matches roman numbers
            return match.group(0).strip()

    @staticmethod
    @abstractmethod
    def episode(word: str) -> int:
        pass

    @staticmethod
    @abstractmethod
    def media_name(word: str) -> str:
        pass

    @staticmethod
    @clean_strings
    def extension(word: str) -> str:
        return word.split('.')[-1]


