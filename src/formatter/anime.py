import re
from typing import List

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
        exceptions = ['no', 'san', 'and', 'to', 'of', 'the', 'in'] \
                     + [el.name for el in RomanNumbers] \
                     + (exceptions or [])
        word_list = re.split(' ', word)
        final = [word_list[0].capitalize()]
        for word in word_list[1:]:
            final.append(word if word in exceptions else word.capitalize())
        return ' '.join(final)

    def new_name(self, item: MediaItem, parser: Parser) -> str:
        match item:
            case Episode():
                # TODO: should contain season
                pattern = '{media_name} - {episode:02d} - {episode_name}.{extension}'
                return self.titlecase(self.format(item, parser, pattern=pattern, lang='ja'))
            case Season():
                return self.titlecase(self.format(item, parser, pattern='{media_name} {season_name}', lang='ja'))
            case Show():
                return self.titlecase(self.format(item, parser, pattern='{media_name}', lang='ja'))

    def format(self, item: MediaItem, parser: Parser, pattern: str, lang: str = 'en') -> str:
        season_name = parser.season_name(item) if not isinstance(item, Show) else None

        pattern = self.__remove_episode_if_required(item, pattern)
        pattern = self.__remove_season_if_required(item, parser, season_name, pattern, lang=lang)

        media_name = episode = episode_name = season = None
        if '{media_name}' in pattern:
            media_name = parser.media_name(item, lang=lang)
        if re.search(r'\{episode(:\d+d)?}', pattern):
            episode = parser.episode(item)
        if '{episode_name}' in pattern:
            episode_name = parser.episode_name(item)
        if '{season}' in pattern:
            season = parser.season(item)

        return pattern.format(
            media_name=media_name,
            media_title=parser.media_title(item, lang=lang),
            season=season,
            season_name=season_name,
            episode=episode,
            episode_name=episode_name,
            extension=parser.extension(item),
        )

    @staticmethod
    def __remove_season_if_required(
            item: MediaItem, parser: Parser, season_name: str, pattern: str, lang: str = 'en'
    ) -> str:
        if isinstance(item, Show) or parser.season(item) <= 1 or not season_name \
                or ('{media_name}' in pattern and season_name in parser.media_name(item, lang=lang)):
            pattern = re.sub(r'( S(eason)?)? ?{season(_name)?} ?', '', pattern).strip()
            pattern = re.sub(r' +', ' ', pattern).strip()
        return pattern

    @staticmethod
    def __remove_episode_if_required(item: MediaItem, pattern: str) -> str:
        if isinstance(item, Show) or isinstance(item, Season):
            pattern = re.sub(r'( E(pisode)?)? ?{episode(_name)?(:\d+d)?} ?', '', pattern).strip()
            pattern = re.sub(r' +', ' ', pattern).strip()
        return pattern

    @staticmethod
    def __metadata(item: MediaItem) -> AnimeMetadata:
        metadata = item.metadata
        assert isinstance(metadata, AnimeMetadata)
        return metadata
