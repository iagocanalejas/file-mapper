import logging
import re
from typing import List

from src.core import MediaType
from src.parsers._parser import Parser
from src.utils.string import clean_strings, remove_tracker, remove_parenthesis, RomanNumbers, apply_clean, \
    generic_clean, remove_extension

logger = logging.getLogger()


class AnimeParser(Parser, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.ANIME, **kwargs)
        return cls._instance

    @staticmethod
    def titlecase(word: str, exceptions: List[str] = None) -> str:
        exceptions = ['no', 'san', 'and', 'to'] + [el.name for el in RomanNumbers] + (exceptions or [])
        word_list = re.split(' ', word)
        final = [word_list[0].capitalize()]
        for word in word_list[1:]:
            final.append(word if word in exceptions else word.capitalize())
        return ' '.join(final)

    @staticmethod
    @clean_strings
    def media_name(word: str) -> str:
        return remove_parenthesis(remove_tracker(word)).strip()

    @staticmethod
    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_parenthesis, remove_extension])
    def episode(word: str) -> int:
        if '-' in word:
            word = word.split('-')[1].strip()

        match = re.search(r'S\d+E\d+', word, re.IGNORECASE)
        if match is not None:
            # Matches S1E1
            return int(re.findall(r'\d+', match.group(0))[1])

        match = re.search(r'E\d -', word, re.IGNORECASE)
        if match is not None:
            # Matches E1 -
            return int(re.findall(r'\d+', match.group(0))[0])

        # Returns first number found
        return int(re.findall(r'\d+', word)[-1])

    def matches(self, name: str, **kwargs) -> bool:
        """
       Checks if the stream is an anime show
       """
        return self.__full_match(name) or self.__partial_match(name)

    @clean_strings
    def __full_match(self, name: str) -> bool:
        try:
            re.search(
                r'\[(\w+-?)*](\s\w+)*\s(.?\s)?(\d{0,3}|E\w{0,6}.?\d{0,3})\s?\(?\[?(\d{3,4}p|.*)\)?]?',
                name,
                re.IGNORECASE
            ).group(0)

            logger.debug(f'{self._class_name}: \'{name}\' matches full regex')
            return True
        except AttributeError:
            return False

    @clean_strings
    def __partial_match(self, name: str) -> bool:
        try:
            re.search(r'(^\[(\w+(\s?|-|.?))+])', name, re.IGNORECASE).group(0)
            re.search(r'-(.?)\d{1,3}|(x|E(pisode)?)(\s|\.|-)?\d{1,3}', name, re.IGNORECASE).group(0)

            logger.debug(f'{self._class_name}: \'{name}\' matches partial regex')
            return True
        except AttributeError:
            return False
