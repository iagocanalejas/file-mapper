import logging
import os
import re
from typing import List, Tuple, Callable

import settings
from src.core.models import Show, Season, Episode, MediaItem
from src.core.models.metadata import AnimeMetadata
from src.datasources.api import MalAPI, AnilistAPI
from src.datasources.datasource import API
from src.datasources.scrapper import WikipediaScrapper
from src.matchers import MediaType
from src.processors import Processor
from src.utils.strings import closest_result, remove_season

logger = logging.getLogger()


class AnimeProcessor(Processor, media_type=MediaType.ANIME):
    _instance = None
    _finders: List[Tuple[API, Callable[[MediaItem], str]]]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **_):
        super(AnimeProcessor, self).__init__()
        self._finders = [
            (MalAPI(parser=self.parser), self.__mal_search_keyword),
            (AnilistAPI(parser=self.parser), self.__anilist_search_keyword),
        ]

    def process_episode(self, episode: Episode):
        super(AnimeProcessor, self).process_episode(episode)

        metadata = [finder.get_anime_details(anime_id=finder.find_anime(fn(episode))) for finder, fn in self._finders]
        episode.metadata = self.__aggregate_metadata(episode, metadata)

        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_episode_name(episode)

        self.rename(episode)

    def process_season(self, season: Season):
        super(AnimeProcessor, self).process_season(season)

        metadata = [finder.get_anime_details(anime_id=finder.find_anime(fn(season))) for finder, fn in self._finders]
        season.metadata = self.__aggregate_metadata(season, metadata)

        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_season_names(season)

        self.rename(season)

    def process_show(self, show: Show):
        super(AnimeProcessor, self).process_show(show)

        metadata = [finder.get_anime_details(anime_id=finder.find_anime(fn(show))) for finder, fn in self._finders]
        show.metadata = self.__aggregate_metadata(show, metadata)

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
            os.rename(item.path, os.path.join(item.base_path, self.formatter.new_name(item, self.parser)))

        super(AnimeProcessor, self).rename(item)

    ########################
    #     First Level      #
    ########################
    # parser.media_name should be none
    ########################

    def __aggregate_metadata(self, item: MediaItem, metadata: List[AnimeMetadata]) -> AnimeMetadata:
        pattern = '{media_title} Season {season}'
        if isinstance(item, Show):
            pattern = '{media_title}'
        media_name = self.formatter.format(item, self.parser, pattern=pattern)

        return AnimeMetadata(
            datasource_id=[m.datasource_id for m in metadata],
            datasource=[m.datasource for m in metadata],
            title=closest_result(media_name, [m.title for m in metadata]),
            alternative_titles={k: v for m in metadata for k, v in m.alternative_titles.items()},
            season_name=next((s for s in [m.season_name for m in metadata] if s is not None), None),
            episode_name=next((s for s in [m.episode_name for m in metadata] if s is not None), None),
        )

    def __mal_search_keyword(self, item: MediaItem) -> str:
        pattern = '{media_title} S{season}'
        if isinstance(item, Show):
            pattern = '{media_title}'
        return self.formatter.format(item, self.parser, pattern=pattern)

    def __anilist_search_keyword(self, item: MediaItem) -> str:
        pattern = '{media_title} Season {season}'
        if isinstance(item, Show):
            pattern = '{media_title}'
        return self.formatter.format(item, self.parser, pattern=pattern)

    ########################
    #     Second Level     #
    ########################
    # parser.media_name should be used
    ########################

    def __wikipedia_search_keyword(self, item: MediaItem, lang: str = 'en') -> str:
        media_name = self.parser.media_name(item, lang=lang)
        media_name = remove_season(media_name)  # This removes S2, Season 2
        if not isinstance(item, Show):
            season_name = self.parser.season_name(item)
            if season_name is not None:
                media_name = media_name.replace(season_name, '').strip()
        return re.sub(r"\s", "_", media_name)
