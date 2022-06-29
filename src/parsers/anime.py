import logging
import re
from typing import Optional

from src.core.models import MediaItem, Show, Season
from src.core.models.metadata import AnimeMetadata
from src.matchers import MediaType
from src.parsers._parser import Parser
from src.utils.strings import remove_tracker, remove_parenthesis, RomanNumbers, apply_clean, \
    generic_clean, remove_extension, apply, remove_episode

logger = logging.getLogger()


class AnimeParser(Parser, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.ANIME, **kwargs)
        return cls._instance

    def episode(self, item: MediaItem) -> int:
        if isinstance(item, Show):
            raise Exception(f'show {item} can\'t have episode')
        if isinstance(item, Season):
            raise Exception(f'season {item} can\'t have episode')
        return self._parse_episode(item.item_name)

    def episode_name(self, item: MediaItem) -> Optional[str]:
        if isinstance(item, Show):
            raise Exception(f'show {item} can\'t have episode')
        if isinstance(item, Season):
            raise Exception(f'season {item} can\'t have episode')
        if item.metadata is not None:
            metadata = item.metadata
            assert isinstance(metadata, AnimeMetadata)
            return metadata.episode_name
        # TODO: Try to parse an episode name from the file name

    def season(self, item: MediaItem) -> int:
        if isinstance(item, Show):
            raise Exception(f'show {item} can\'t have season')
        return self._parse_season(item.item_name)

    def season_name(self, item: MediaItem) -> Optional[str]:
        if isinstance(item, Show):
            raise Exception(f'show {item} can\'t have season')
        if item.metadata is not None:
            metadata = item.metadata
            assert isinstance(metadata, AnimeMetadata)
            return metadata.season_name
        return self._parse_season_name(item.item_name)

    def media_name(self, item: MediaItem, lang: str = 'en') -> str:
        if item.metadata is not None:
            metadata = item.metadata
            assert isinstance(metadata, AnimeMetadata)
            return metadata.media_name(lang)

        return apply(
            functions=[generic_clean, remove_tracker, remove_parenthesis, remove_extension, remove_episode],
            arg=item.item_name
        )
        # TODO: do more cleans @test_media_name_no_metadata

    def is_seasoned_media_name(self, item: MediaItem) -> bool:
        media_name = self.media_name(item)
        return self._parse_season_name(media_name) is not None

    @staticmethod
    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_parenthesis, remove_extension])
    def _parse_episode(word: str) -> int:
        if '-' in word:
            word = word.split('-')[1].strip()

        match = re.search(r'S\d+E\d+', word, re.IGNORECASE)
        if match is not None:
            # Matches S1E1
            return int(re.findall(r'\d+', match.group(0))[1])

        match = re.search(r'E\d+', word, re.IGNORECASE)
        if match is not None:
            # Matches E1 -
            return int(re.findall(r'\d+', match.group(0))[0])
        # Returns first number found
        return int(re.findall(r'\d+', word)[-1])

    @staticmethod
    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_parenthesis, remove_extension])
    def _parse_season(word: str) -> int:
        match = re.search(r'Season \d+', word, re.IGNORECASE)
        if match is not None:
            # Matches Season 1
            s_re = re.compile(r'season ', re.IGNORECASE)
            return int(s_re.sub('', match.group(0)))

        match = re.search(r'S\d+E\d+', word, re.IGNORECASE)
        if match is not None:
            # Matches S1E1
            return int(re.findall(r'\d+', match.group(0))[0])

        match = re.search(r'S\d+ -', word, re.IGNORECASE)
        if match is not None:
            # Matches S1 -
            return int(re.findall(r'\d+', match.group(0))[0])

        match = re.search(r'S\d+$', word, re.IGNORECASE)
        if match is not None:
            # Matches S1
            return int(re.findall(r'\d+', match.group(0))[0])

        match = re.search(r' (IX|IV|V?I{0,3})( |$)', word)
        if match is not None:
            # Matches roman numbers
            return RomanNumbers[match.group(0).strip()].value

        return 1

    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_parenthesis, remove_extension])
    def _parse_season_name(self, word: str) -> Optional[str]:
        match = re.search(r' (IX|IV|V?I{0,3})( |$)', word)
        if match is not None:
            # Matches roman numbers
            return match.group(0).strip()

        season = self._parse_season(word)
        if season > 1:
            return f'S{season}'
