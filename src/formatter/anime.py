import re
from typing import List, Optional

from src.core.exceptions import MediaTypeException
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

    def new_name(self, item: MediaItem, parser: Parser) -> str:
        match item:
            case Episode():
                assert isinstance(item, Episode)
                return self.__episode_new_name(item, parser)
            case Season() | Show():
                return self.titlecase(parser.media_name(item, lang='ja'))

    def format(self, item: MediaItem, parser: Parser, pattern: str, lang: str = 'en') -> str:
        if '{season}' in pattern and isinstance(item, Show):
            raise MediaTypeException(f'item {item} can\'t have season')
        if '{episode}' in pattern and (isinstance(item, Show) or isinstance(item, Season)):
            raise MediaTypeException(f'item {item} can\'t have episode')

        if parser.season(item) <= 1:
            pattern = re.sub(r' S(eason)? ?{season(_name)?} ?', '', pattern).strip()
            pattern = re.sub(r' +', ' ', pattern).strip()

        media_name = episode = episode_name = season = season_name = None
        if '{media_name}' in pattern:
            media_name = parser.media_name(item, lang=lang),
        if '{episode}' in pattern:
            episode = parser.episode(item)
        if '{episode_name}' in pattern:
            episode_name = parser.episode_name(item)
        if '{season}' in pattern:
            season = parser.season(item)
        if '{season_name}' in pattern:
            season_name = parser.season_name(item)

        return pattern.format(
            media_name=media_name,
            media_title=parser.media_title(item, lang=lang),
            season=season,
            season_name=season_name,
            episode=episode,
            episode_name=episode_name,
            extension=parser.extension(item),
        )

    def __episode_new_name(self, item: Episode, parser: Parser) -> str:
        title = self.titlecase(parser.media_name(item, lang='ja'))
        episode = parser.episode(item)
        episode_name = self.titlecase(parser.episode_name(item))
        extension = parser.extension(item)
        return f'{title} - {episode:02d} - {episode_name}.{extension}'

    @staticmethod
    def __metadata(item: MediaItem) -> AnimeMetadata:
        metadata = item.metadata
        assert isinstance(metadata, AnimeMetadata)
        return metadata
