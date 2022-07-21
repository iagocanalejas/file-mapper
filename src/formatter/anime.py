import os.path
import re
from typing import List

from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.types import Language
from src.formatter._formatter import Formatter
from src.matchers import MediaType
from src.parsers import Parser
from src.utils.strings import clean_output
from src.utils.strings import RomanNumbers


class AnimeFormatter(Formatter, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.ANIME, **kwargs)
        return cls._instance

    @staticmethod
    def titlecase(word: str, exceptions: List[str] = None, **kwargs) -> str:
        exceptions = ['no', 'san', 'and', 'to', 'of', 'the', 'in', 'de'] \
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
                pattern = '{media_name} {season_name} - {episode:02d}.{episode_part}'
                title = self.format(item, parser, pattern=pattern, lang=Language.JA)
                episode = self.format(item, parser, pattern='{episode_name}.{extension}', lang=Language.JA)
                return clean_output(f'{title} - {episode}')
            case Season():
                title = self.format(item, parser, pattern='{media_name} {season_name}', lang=Language.JA)
                return clean_output(self.titlecase(title))
            case Show():
                return clean_output(self.titlecase(self.format(item, parser, pattern='{media_name}', lang=Language.JA)))

    def format(self, item: MediaItem, parser: Parser, pattern: str, lang: Language = Language.EN) -> str:
        season_name = parser.season_name(item) if not isinstance(item, Show) else None

        pattern = self.__remove_episode_if_required(item, pattern)
        pattern = self.__remove_episode_part_if_required(item, parser, pattern)
        pattern = self.__remove_season_if_required(item, parser, season_name, pattern, lang=lang)

        media_name = episode = episode_name = episode_part = season = None
        if '{media_name}' in pattern:
            media_name = parser.media_name(item, lang=lang)
        if re.search(r'\{episode(:\d+d)?}', pattern):
            episode = parser.episode(item)
        if '{episode_name}' in pattern:
            episode_name = parser.episode_name(item)
        if '{episode_part}' in pattern:
            episode_part = parser.episode_part(item)
        if '{season}' in pattern:
            season = parser.season(item)

        return pattern.format(
            media_name=media_name,
            media_title=parser.media_title(item),
            season=season,
            season_name=season_name,
            episode=episode,
            episode_part=episode_part,
            episode_name=episode_name,
            extension=parser.extension(item),
        )

    @staticmethod
    def __remove_season_if_required(
            item: MediaItem, parser: Parser, season_name: str, pattern: str, lang: Language = Language.EN
    ) -> str:
        season = parser.season(item) if not isinstance(item, Show) else None
        should_remove_season = False
        if not season or not season_name:
            should_remove_season = True
        elif season <= 1 and re.match(r'^S(eason )?\d+$', season_name, re.IGNORECASE):
            # No meaningful season name for season 1
            should_remove_season = True
        elif '{media_name}' in pattern:
            media_name = parser.media_name(item, lang=lang)
            re_se = f'S(eason )?{season}'
            if re.search(re_se, media_name, re.IGNORECASE) or re.search(season_name, media_name, re.IGNORECASE):
                # Season name is already contained in the media_name
                should_remove_season = True

        if should_remove_season:
            pattern = re.sub(r'( S(eason)?)? ?{season(_name)?}', '', pattern).strip()
            pattern = re.sub(r' +', ' ', pattern).strip()
        return pattern

    @staticmethod
    def __remove_episode_if_required(item: MediaItem, pattern: str) -> str:
        if isinstance(item, Show) or isinstance(item, Season):
            pattern = re.sub(r'( E(pisode)?)? ?{episode(_name)?(:\d+d)?}', '', pattern).strip()
            pattern = re.sub(r' +', ' ', pattern).strip()
        return pattern

    @staticmethod
    def __remove_episode_part_if_required(item: MediaItem, parser: Parser, pattern: str) -> str:
        if not isinstance(item, Episode) or parser.episode_part(item) is None:
            pattern = re.sub(r'\.\{episode_part}', '', pattern).strip()
        return pattern
