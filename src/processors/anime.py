import logging
import os
from typing import Callable
from typing import List
from typing import Tuple

from src import settings
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.models.metadata import AnimeMetadata
from src.datasources.api import AnilistAPI
from src.datasources.api import MalAPI
from src.datasources.datasource import API
from src.datasources.scrapper import WikipediaScrapper
from src.matchers import MediaType
from src.processors import Processor
from src.utils.strings import closest_result

logger = logging.getLogger()


class AnimeProcessor(Processor, media_type=MediaType.ANIME):
    _instance = None
    _finders: List[Tuple[API, Callable[[MediaItem], str]]]

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **_):
        super().__init__()
        self._finders = [
            (MalAPI(parser=self.parser), self.__format),
            (AnilistAPI(parser=self.parser), self.__format),
        ]

    def process_episode(self, episode: Episode):
        super().process_episode(episode)

        self.__fill_metadata(episode)
        WikipediaScrapper(parser=self.parser).fill_episode_name(episode)

        self.rename(episode)

    def process_season(self, season: Season):
        super().process_season(season)

        self.__fill_metadata(season)
        WikipediaScrapper(parser=self.parser).fill_season_names(season)

        self.rename(season)

    def process_show(self, show: Show):
        super().process_show(show)

        self.__fill_metadata(show)
        WikipediaScrapper(parser=self.parser).fill_show_names(show)

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

        super().rename(item)

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
