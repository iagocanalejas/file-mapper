import logging
from typing import List, Callable

from src.core.models import Episode, Season, Show, MediaItem
from src.datasources._datasource import Scrapper
from src.datasources.exceptions import NotFound
from src.datasources.scrapper.wikipedia.pages import WikipediaEpisodePage, WikipediaMainPage, WikipediaPage
from src.parsers import Parser

logger = logging.getLogger()


class WikipediaScrapper(Scrapper):
    BASE_EPISODE_URL = 'https://en.wikipedia.org/wiki/List_of_{}_episodes'
    BASE_MAIN_URL = 'https://en.wikipedia.org/wiki/{}#Episode_list'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    def __init__(self, parser: Parser, keyword_fn: Callable[[MediaItem], str]):
        super(WikipediaScrapper, self).__init__(parser)
        self.keyword_fn = keyword_fn

    def fill_show_names(self, show: Show) -> Show:
        logger.info(f'{self._class}:: searching for show :: {self.keyword_fn(show)}')

        page = self.__load_page(self.keyword_fn(show))
        season_files = [f for s in [s.episodes for s in show.seasons] for f in s]
        self.__fill_episodes(page, show.episodes + season_files)
        self.__fill_seasons(page, show.seasons)

        return show

    def fill_season_names(self, season: Season) -> Season:
        """
        Retrieves the season episodes names.
        :param season: to fill file names
        :return: The season with the updated files
        """

        logger.info(f'{self._class}:: searching for season :: {self.keyword_fn(season)}')

        page = self.__load_page(self.keyword_fn(season))
        self.__fill_episodes(page, season.episodes)
        self.__fill_seasons(page, [season])

        return season

    def fill_episode_name(self, file: Episode) -> Episode:
        """
        Retrieves the episode name for the given file.
        :param file: to fill episode name
        :return: Returns the file with the new episode name
        """

        logger.info(f'{self._class}:: searching for episode :: {self.keyword_fn(file)}')

        page = self.__load_page(self.keyword_fn(file))
        self.__fill_episodes(page, [file])

        return file

    def __load_page(self, search_keyword: str) -> WikipediaPage:
        page = WikipediaEpisodePage(search_keyword)
        if not page.is_valid:
            page = WikipediaMainPage(search_keyword)
        if not page.is_valid:
            raise NotFound(f"{self._class}:: matching page for :: {search_keyword}")
        return page

    def __fill_episodes(self, page: WikipediaPage, episodes: List[Episode]):
        not_found = []

        for episode in episodes:
            episode_name = page.episode_name(self.parser.season(episode), self.parser.episode(episode))
            if episode_name is None:
                not_found.append(episode)

            episode.metadata.episode_name = episode_name

        logger.info(f'{self._class}:: NOT FOUND :: episode names :: {[s.item_name for s in not_found]}')

    def __fill_seasons(self, page: WikipediaPage, seasons: List[Season]):
        not_found = []

        for season in seasons:
            season_name = page.season_name(self.parser.season(season))
            if season_name is None:
                not_found.append(season)

            season.metadata.season_name = season_name

        logger.info(f'{self._class}:: NOT FOUND :: season names :: {[s.item_name for s in not_found]}')
