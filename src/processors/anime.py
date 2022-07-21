import logging
import os
from typing import List
from typing import Optional
from typing import Tuple

from src import settings
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.models.metadata import AnimeMetadata
from src.core.types import Language
from src.datasources.api import AnilistAPI
from src.datasources.api import ImdbAPI
from src.datasources.api import MalAPI
from src.datasources.datasource import AnimeDatasource
from src.datasources.datasource import API
from src.datasources.exceptions import NotFound
from src.datasources.scrapper import ImdbScrapper
from src.datasources.scrapper import WikipediaScrapper
from src.matchers import MediaType
from src.processors import Processor
from src.utils.strings import closest_result

logger = logging.getLogger()


class AnimeProcessor(Processor, media_type=MediaType.ANIME):
    _instance = None
    _apis: List[API]
    _scrappers: List[AnimeDatasource]

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **_):
        super().__init__()
        self._apis = [
            MalAPI(parser=self.parser),
            AnilistAPI(parser=self.parser),
            ImdbAPI(parser=self.parser),
        ]
        self._scrappers = [
            WikipediaScrapper(parser=self.parser),
            ImdbScrapper(parser=self.parser, format_fn=self.__format),
        ]

    def process_episode(self, episode: Episode):
        logger.info(f'{self._class}:: processing episode :: {episode}')

        self.__fill_metadata(episode)

        exceptions = []
        for scrapper in self._scrappers:
            try:
                scrapper.fill_episode_name(episode)
            except NotFound as e:
                exceptions.append(e)
                continue
            else:
                self.rename(episode)
                return

        logger.error(f'{self._class}:: NOT FOUND')
        [logger.error(f'\t{e}') for e in exceptions]

    def process_season(self, season: Season):
        logger.info(f'{self._class}:: processing season :: {season}')

        self.__fill_metadata(season)

        exceptions = []
        for scrapper in self._scrappers:
            try:
                scrapper.fill_season_names(season)
            except NotFound as e:
                exceptions.append(e)
                continue
            else:
                self.rename(season)
                return

        logger.error(f'{self._class}:: NOT FOUND')
        [logger.error(f'\t{e}') for e in exceptions]

    def process_show(self, show: Show):
        logger.info(f'{self._class}:: processing show :: {show}')

        self.__fill_metadata(show)

        exceptions = []
        for scrapper in self._scrappers:
            try:
                scrapper.fill_show_names(show)
            except NotFound as e:
                exceptions.append(e)
                continue
            else:
                self.rename(show)
                return

        logger.error(f'{self._class}:: NOT FOUND')
        [logger.error(f'\t{e}') for e in exceptions]

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
        season = self.parser.season(item) if not isinstance(item, Show) else 1
        season_name = self.parser.season_name(item) if not isinstance(item, Show) else None
        metadata = [api.search_anime(self.__format(item), item.language, season, season_name) for api in self._apis]
        metadata = self.__aggregate_metadata(item, metadata)

        logger.info(f'{self._class}:: aggregated metadata :: {metadata}')
        item.metadata = metadata

    # TODO: Improve data aggregation
    def __aggregate_metadata(self, item: MediaItem, metadata: List[Optional[AnimeMetadata]]) -> AnimeMetadata:
        metadata = [m for m in metadata if m is not None]  # filter nulls
        media_name = self.formatter.format(item, self.parser, pattern='{media_title} {season_name}')
        title_lang, title = self.__retrieve_closest_title(media_name, metadata)

        return AnimeMetadata(
            datasource_data={k: v for m in metadata for k, v in m.datasource_data.items()},
            title=title,
            title_lang=title_lang,
            alternative_titles={k: v for m in metadata for k, v in m.alternative_titles.items() if v},
            season_name=next(iter([m.season_name for m in metadata]), None),
            episode_name=next(iter([m.episode_name for m in metadata]), None),
        )

    @staticmethod
    def __retrieve_closest_title(media_name: str, metadata: List[AnimeMetadata]) -> Tuple[Language, str]:
        ja_metadata = [m for m in metadata if m.title_lang == Language.JA]
        if ja_metadata:
            return Language.JA, closest_result(media_name, [m.media_name(Language.JA) for m in ja_metadata])
        return Language.EN, closest_result(media_name, [m.media_name(Language.EN) for m in metadata])
