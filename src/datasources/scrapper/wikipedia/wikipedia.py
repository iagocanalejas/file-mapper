import asyncio
import logging
import re
from typing import List
from typing import Tuple

import aiohttp

from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.models.config import GlobalConfig
from src.core.models.metadata import as_anime
from src.core.types import DatasourceName
from src.core.types import Language
from src.datasources.datasource import AnimeDatasource
from src.datasources.datasource import Scrapper
from src.datasources.exceptions import InvalidConfiguration
from src.datasources.exceptions import NotFound
from src.datasources.scrapper.wikipedia.pages import WikipediaEpisodePage
from src.datasources.scrapper.wikipedia.pages import WikipediaMainPage
from src.datasources.scrapper.wikipedia.pages import WikipediaPage
from src.utils.strings import remove_parenthesis
from src.utils.strings import remove_season

logger = logging.getLogger()


class WikipediaScrapper(Scrapper, AnimeDatasource):
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

    async def __load_page(self, item: MediaItem, languages: List[Language] = None) -> WikipediaPage:
        keywords, pages = self.__get_preconfigured_pages() \
            if GlobalConfig().wikipedia_url \
            else self.__get_pages(item, languages)

        async with aiohttp.ClientSession() as session:
            pages = await asyncio.gather(*[page.load(session) for page in pages], return_exceptions=True)

        try:
            page = next(p for p in pages if p.is_valid)
            logger.info(f'{self._class}:: valid page :: {page}')
            return page
        except StopIteration:
            raise NotFound(f'{self._class}:: matching page for :: {keywords}')

    def __fill_episodes(self, page: WikipediaPage, episodes: List[Episode]):
        not_found = []

        for episode in episodes:
            episode_name = page.episode_name(
                episode.parsed.season,
                episode.parsed.episode,
                episode.parsed.episode_part,
            )
            if episode_name is None:
                not_found.append(episode)
                continue

            episode.metadata.episode_name = episode_name

        logger.info(f'{self._class}:: NOT FOUND :: episode names :: {[s.item_name for s in not_found]}')

    def __fill_seasons(self, page: WikipediaPage, seasons: List[Season]):
        not_found = []

        for season in seasons:
            season_name = page.season_name(season.parsed.season)
            if season_name is None:
                not_found.append(season)
                continue

            season.metadata.season_name = self.__patch_season_name(page, remove_parenthesis(season_name))

        logger.info(f'{self._class}:: NOT FOUND :: season names :: {[s.item_name for s in not_found]}')

    def __get_pages(self, item: MediaItem, languages: List[Language]) -> Tuple[List[str], List[WikipediaPage]]:
        if languages is None:
            languages = [Language.EN, Language.JA]

        keywords = [self.__search_keyword(item, lang) for lang in languages]
        pages = [
            [WikipediaEpisodePage(keyword=keyword), WikipediaMainPage(keyword=keyword)]
            for keyword in keywords
        ]
        return keywords, [x for xs in pages for x in xs]  # flatten list

    @staticmethod
    def __get_preconfigured_pages() -> Tuple[List[str], List[WikipediaPage]]:
        if WikipediaEpisodePage.check_url(GlobalConfig().wikipedia_url):
            pages = [WikipediaEpisodePage(url=GlobalConfig().wikipedia_url)]
        elif WikipediaMainPage.check_url(GlobalConfig().wikipedia_url):
            pages = [WikipediaMainPage(url=GlobalConfig().wikipedia_url)]
        else:
            raise InvalidConfiguration(GlobalConfig().wikipedia_url)

        return [GlobalConfig().wikipedia_url], pages

    @staticmethod
    def __patch_season_name(page: WikipediaPage, season_name: str) -> str:
        match = re.match(page.title(), season_name, re.IGNORECASE)
        if match is not None:
            return season_name.replace(match.group(0), '').strip()
        return season_name

    @staticmethod
    def __search_keyword(item: MediaItem, lang: Language = Language.EN) -> str:
        # TODO: wikipedia URLs are case sensitive
        media_name = as_anime(item.metadata).media_name(lang=lang)
        media_name = re.sub(r'[_!]+', '', media_name)
        media_name = remove_season(media_name)  # this removes S2, Season 2
        if not isinstance(item, Show):
            season_name = item.parsed.season_name
            if season_name is not None:
                media_name = media_name.replace(season_name, '').strip()  # this removes the season name
        return re.sub(r'\s', '_', media_name)
