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

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **_):
        super(AnimeProcessor, self).__init__()
        self._finders = [
            (MalAPI(parser=self.parser), self.__format),
            (AnilistAPI(parser=self.parser), self.__format),
        ]

    def process_episode(self, episode: Episode):
        super(AnimeProcessor, self).process_episode(episode)

        self.__fill_metadata(episode)
        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_episode_name(episode)

        self.rename(episode)

    def process_season(self, season: Season):
        super(AnimeProcessor, self).process_season(season)

        self.__fill_metadata(season)
        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_season_names(season)

        self.rename(season)

    def process_show(self, show: Show):
        super(AnimeProcessor, self).process_show(show)

        self.__fill_metadata(show)
        WikipediaScrapper(parser=self.parser, keyword_fn=self.__wikipedia_search_keyword).fill_show_names(show)

        self.rename(show)

    def rename(self, item: MediaItem):
        if isinstance(item, Season):
            for f in item.episodes:
                self.rename(f)
        if isinstance(item, Show):
            for s in item.seasons:
                self.rename(s)
            for f in item.episodes:
                self.rename(f)

        if not settings.MOCK_RENAME:
            os.rename(item.path, os.path.join(item.base_path, self.formatter.new_name(item, self.parser)))

        super(AnimeProcessor, self).rename(item)

    ########################
    #    Search Format     #
    ########################

    def __format(self, item: MediaItem):
        return self.formatter.format(item, self.parser, pattern='{media_title}')

    ########################
    #     First Level      #
    ########################

    def __fill_metadata(self, item: MediaItem):
        season = self.parser.season(item) if not isinstance(item, Show) else 0
        season_name = self.parser.season_name(item) if not isinstance(item, Show) else None
        metadata = [finder.search_anime(fn(item), season, season_name) for finder, fn in self._finders]
        metadata = self.__aggregate_metadata(item, metadata)

        logger.info(f'{self._class}:: aggregated metadata :: {metadata}')
        item.metadata = metadata

    def __aggregate_metadata(self, item: MediaItem, metadata: List[AnimeMetadata]) -> AnimeMetadata:
        media_name = self.formatter.format(item, self.parser, pattern='{media_title} {season_name}')

        return AnimeMetadata(
            datasource_id=[m.datasource_id for m in metadata],
            datasource=[m.datasource for m in metadata],
            title=closest_result(media_name, [m.title for m in metadata]),
            alternative_titles={k: v for m in metadata for k, v in m.alternative_titles.items() if v},
            season_name=next(iter([m.season_name for m in metadata]), None),
            episode_name=next(iter([m.episode_name for m in metadata]), None),
        )

    ########################
    #     Second Level     #
    ########################

    def __wikipedia_search_keyword(self, item: MediaItem, lang: str = 'en') -> str:
        # TODO: should titlecase the keyword ignoring some words. The 'Yuri on Ice' problem
        media_name = self.parser.media_name(item, lang=lang)
        media_name = re.sub(r'[_!]+', '', media_name)
        media_name = remove_season(media_name)  # this removes S2, Season 2
        if not isinstance(item, Show):
            season_name = self.parser.season_name(item)
            if season_name is not None:
                media_name = media_name.replace(season_name, '').strip()  # this removes the season name
        return re.sub(r"\s", "_", media_name)
