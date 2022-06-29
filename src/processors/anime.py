import logging
import os
import re

import settings
from src.core.models import Show, Season, Episode, MediaItem
from src.datasources.api import MalAPI
from src.datasources.scrapper import WikipediaScrapper
from src.processors import Processor
from src.matchers import MediaType
from src.utils.strings import generic_clean

logger = logging.getLogger()


class AnimeProcessor(Processor, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def process_episode(self, episode: Episode):
        super(AnimeProcessor, self).process_episode(episode)

        finder = MalAPI(parser=self.parser)
        episode.metadata = finder.get_anime_details(anime_id=finder.find_anime(self.__mal_search_keyword(episode)))
        episode.metadata.seasoned = self.parser.is_seasoned_media_name(episode)

        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_episode_name(episode)

        self.rename(episode)

    def process_season(self, season: Season):
        super(AnimeProcessor, self).process_season(season)

        finder = MalAPI(parser=self.parser)
        season.metadata = finder.get_anime_details(anime_id=finder.find_anime(self.__mal_search_keyword(season)))
        season.metadata.seasoned = self.parser.is_seasoned_media_name(season)

        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_season_names(season)

        self.rename(season)

    def process_show(self, show: Show):
        super(AnimeProcessor, self).process_show(show)

        finder = MalAPI(parser=self.parser)
        show.metadata = finder.get_anime_details(anime_id=finder.find_anime(self.__mal_search_keyword(show)))

        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_show_names(show)

        self.rename(show)

    def rename(self, item: MediaItem):
        if isinstance(item, Season):
            for f in item.episodes:
                self.rename(f)
        if isinstance(item, Show):
            for f in item.episodes:
                self.rename(f)
            for s in item.seasons:
                self.rename(s)

        if not settings.MOCK_RENAME:
            os.rename(item.path, os.path.join(item.base_path, self.formatter.new_name(self.parser, item)))

        super(AnimeProcessor, self).rename(item)

    def __mal_search_keyword(self, item: MediaItem) -> str:
        media_name = self.parser.media_name(item)
        if isinstance(item, Show):
            return f'{media_name}'
        season = self.parser.season_name(item)
        return f'{media_name} {season}' if season and season not in media_name else f'{media_name}'

    def __wikipedia_search_keyword(self, item: MediaItem, lang: str = 'en') -> str:
        media_name = self.parser.media_name(item, lang=lang)
        if 'season' in media_name.lower():
            s_re = re.compile(r'season \d+', re.IGNORECASE)
            media_name = generic_clean(s_re.sub('', media_name))
        return media_name.replace(' ', '_')
