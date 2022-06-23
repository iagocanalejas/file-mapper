import re
from typing import List, Optional

from src.core.models import MediaItem, Episode, Season, Show
from src.core.models.metadata import AnimeMetadata
from src.formatter._formatter import Formatter
from src.matchers import MediaType
from src.parsers import Parser
from src.utils.strings import RomanNumbers


class AnimeFormatter(Formatter, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.ANIME, **kwargs)
        return cls._instance

    @staticmethod
    def titlecase(word: str, exceptions: List[str] = None, **kwargs) -> str:
        exceptions = ['no', 'san', 'and', 'to'] + [el.name for el in RomanNumbers] + (exceptions or [])
        word_list = re.split(' ', word)
        final = [word_list[0].capitalize()]
        for word in word_list[1:]:
            final.append(word if word in exceptions else word.capitalize())
        return ' '.join(final)

    def new_name(self, parser: Parser, item: MediaItem) -> str:
        match item:
            case Episode():
                assert isinstance(item, Episode)
                return self.__episode_new_name(parser, item)
            case Season():
                assert isinstance(item, Season)
                return self.__season_new_name(parser, item)
            case Show():
                title = self.titlecase(parser.media_name(item, lang='ja'))
                return f'{title}'

    def __episode_new_name(self, parser: Parser, item: Episode) -> str:
        title = self.titlecase(parser.media_name(item, lang='ja'))
        episode = parser.episode(item)
        episode_name = self.titlecase(parser.episode_name(item))
        extension = parser.extension(item)
        if not self.__metadata(item).seasoned:
            season = self.__get_season(parser, item)
            if season is not None:
                return f'{title} {season} - {episode:02d} - {episode_name}.{extension}'
        return f'{title} - {episode:02d} - {episode_name}.{extension}'

    def __season_new_name(self, parser: Parser, item: Season) -> str:
        title = self.titlecase(parser.media_name(item, lang='ja'))
        if not self.__metadata(item).seasoned:
            season = self.__get_season(parser, item)
            if season is not None:
                return f'{title} {season}'
        return f'{title}'

    def __get_season(self, parser: Parser, item: MediaItem) -> Optional[str]:
        season = parser.season(item)
        if season == 1:
            return None

        season_name = parser.season_name(item)
        if season_name is None:
            season_name = f'S{season}'
        return self.titlecase(season_name)

    @staticmethod
    def __metadata(item: MediaItem) -> AnimeMetadata:
        metadata = item.metadata
        assert isinstance(metadata, AnimeMetadata)
        return metadata
