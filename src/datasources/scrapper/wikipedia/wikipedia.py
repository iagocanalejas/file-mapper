import asyncio
import logging
import re
from typing import List

import aiohttp

from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.types import DatasourceName
from src.datasources.datasource import Scrapper
from src.datasources.exceptions import NotFound
from src.datasources.scrapper.wikipedia.pages import WikipediaEpisodePage
from src.datasources.scrapper.wikipedia.pages import WikipediaMainPage
from src.datasources.scrapper.wikipedia.pages import WikipediaPage
from src.utils.strings import remove_parenthesis
from src.utils.strings import remove_season

logger = logging.getLogger()


class WikipediaScrapper(Scrapper):
    DATASOURCE = DatasourceName.WIKIPEDIA

    def fill_show_names(self, show: Show) -> Show:
        """
        :return: The shou with the updated show, season and episode names
        """

        page = asyncio.run(self.__load_page(show))
        season_files = [f for s in [s.episodes for s in show.seasons] for f in s]
        self.__fill_episodes(page, show.episodes + season_files)
        self.__fill_seasons(page, show.seasons)

        return show

    def fill_season_names(self, season: Season) -> Season:
        """
        :return: The season with updated season and episode names
        """

        page = asyncio.run(self.__load_page(season))
        self.__fill_episodes(page, season.episodes)
        self.__fill_seasons(page, [season])

        return season

    def fill_episode_name(self, episode: Episode) -> Episode:
        """
        :return: Returns the episode with the updated episode name
        """

        page = asyncio.run(self.__load_page(episode))
        self.__fill_episodes(page, [episode])

        return episode

    async def __load_page(self, item: MediaItem, lang: str = 'en') -> WikipediaPage:
        keyword = self.__search_keyword(item, lang=lang)
        keyword_ja = self.__search_keyword(item, lang='ja')
        pages = [
            WikipediaEpisodePage(keyword),
            WikipediaMainPage(keyword),
            WikipediaEpisodePage(keyword_ja),
            WikipediaMainPage(keyword_ja),
        ]
        async with aiohttp.ClientSession() as session:
            pages = await asyncio.gather(*[page.load(session) for page in pages], return_exceptions=True)

        try:
            page = next(p for p in pages if p.is_valid)
            logger.info(f'{self._class}:: valid page :: {page}')
            return page
        except StopIteration:
            raise NotFound(f'{self._class}:: matching page for :: {keyword}')

    def __fill_episodes(self, page: WikipediaPage, episodes: List[Episode]):
        not_found = []

        for episode in episodes:
            episode_name = page.episode_name(
                self.parser.season(episode),
                self.parser.episode(episode),
                self.parser.episode_part(episode),
            )
            if episode_name is None:
                not_found.append(episode)
                continue

            episode.metadata.episode_name = episode_name

        logger.info(f'{self._class}:: NOT FOUND :: episode names :: {[s.item_name for s in not_found]}')

    def __fill_seasons(self, page: WikipediaPage, seasons: List[Season]):
        not_found = []

        for season in seasons:
            season_name = page.season_name(self.parser.season(season))
            if season_name is None:
                not_found.append(season)
                continue

            season.metadata.season_name = self.__patch_season_name(page, remove_parenthesis(season_name))

        logger.info(f'{self._class}:: NOT FOUND :: season names :: {[s.item_name for s in not_found]}')

    @staticmethod
    def __patch_season_name(page: WikipediaPage, season_name: str) -> str:
        match = re.match(page.title(), season_name, re.IGNORECASE)
        if match is not None:
            return season_name.replace(match.group(0), '').strip()
        return season_name

    def __search_keyword(self, item: MediaItem, lang: str = 'en') -> str:
        # TODO: should titlecase the keyword ignoring some words. The 'Yuri on Ice' problem
        media_name = self.parser.media_name(item, lang=lang)
        media_name = re.sub(r'[_!]+', '', media_name)
        media_name = remove_season(media_name)  # this removes S2, Season 2
        if not isinstance(item, Show):
            season_name = self.parser.season_name(item)
            if season_name is not None:
                media_name = media_name.replace(season_name, '').strip()  # this removes the season name
        return re.sub(r'\s', '_', media_name)
