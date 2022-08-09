import logging
import re
from typing import Optional

from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.filemapper.matchers import MediaType
from src.filemapper.parsers._parser import Parser
from src.utils.strings import accepts
from src.utils.strings import apply
from src.utils.strings import apply_clean
from src.utils.strings import generic_clean
from src.utils.strings import remove_episode
from src.utils.strings import remove_episode_name
from src.utils.strings import remove_extension
from src.utils.strings import remove_parenthesis
from src.utils.strings import remove_season
from src.utils.strings import remove_tracker
from src.utils.strings import remove_trailing_hyphen
from src.utils.strings import RomanNumbers

logger = logging.getLogger()


class AnimeParser(Parser, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.ANIME, **kwargs)
        return cls._instance

    @accepts(Episode)
    def episode(self, item: MediaItem) -> int:
        return self._parse_episode(item.item_name)

    @accepts(Episode)
    def episode_part(self, item: MediaItem) -> Optional[int]:
        episode = self.episode(item)
        match = re.search(rf'{episode}\.\d+', item.item_name)
        if match is not None:
            return int(match.group(0).split('.')[1])

    @accepts(Episode, bool)
    def episode_name(self, item: MediaItem, use_metadata: bool = True) -> Optional[str]:
        # TODO: Try to parse an episode name from the file name
        return

    @accepts((Episode, Season))
    def season(self, item: MediaItem) -> int:
        return self._parse_season(item.item_name)

    @accepts((Episode, Season), bool)
    def season_name(self, item: MediaItem, use_metadata: bool = True) -> Optional[str]:
        return self._parse_season_name(item.item_name)

    def media_title(self, item: MediaItem) -> Optional[str]:
        media_title = item.item_name

        # Removes some season names
        if not isinstance(item, Show):
            season_name = self.season_name(item, use_metadata=False)
            if season_name is not None:
                media_title = media_title.replace(season_name, '')

        return apply(
            functions=[
                generic_clean, remove_tracker, remove_parenthesis,
                remove_extension, remove_episode_name, remove_season, remove_episode,
                remove_trailing_hyphen,
            ],
            arg=media_title
        )

    @staticmethod
    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_parenthesis, remove_extension])
    def _parse_episode(word: str) -> int:
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
    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_extension])
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

    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_extension])
    def _parse_season_name(self, word: str) -> Optional[str]:
        match = re.search(r' (IX|IV|V?I{0,3})( |$)', word)
        if match is not None:
            # Matches roman numbers
            return match.group(0).strip()
        # TODO: Try to parse a season name from the file name

        season = self._parse_season(word)
        if season > 1:
            return f'S{season}'
