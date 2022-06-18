import logging

from src.datasources._datasource import Scrapper
from src.datasources.exceptions import NotFound
from src.datasources.scrapper.wikipedia.pages import WikipediaEpisodePage, WikipediaMainPage, WikipediaPage
from src.models import Episode, Season, Show
from src.parsers import Parser
from src.utils.string import generic_clean

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

    def fill_show_names(self, show: Show) -> Show:
        logger.info(f'{self._class_name}:: searching for show :: {self.build_search_keyword(show)}')

        page = self.__load_page(show)
        season_files = [f for s in [s.episodes for s in show.seasons] for f in s]
        not_found = []

        for file in show.files + season_files:
            episode_name = page.episode_name(file.season, file.episode)
            if episode_name is None:
                not_found.append(file)

            file.metadata.episode_name = episode_name

        if not_found:
            logger.error(f'{self._class_name}:: not found show episodes :: {not_found}')
            raise NotFound(f"{self._class_name}:: matching names :: {not_found}")

        logger.info(f'{self._class_name}:: found')
        return show

    def fill_season_names(self, season: Season) -> Season:
        """
        Retrieves the season episodes names.
        :param season: to fill file names
        :return: The season with the updated files
        """

        logger.info(f'{self._class_name}:: searching for season :: {self.build_search_keyword(season)}')

        page = self.__load_page(season)
        not_found = []

        for file in season.episodes:
            episode_name = page.episode_name(file.season, file.episode)
            if episode_name is None:
                not_found.append(file)

            file.metadata.episode_name = episode_name

        if not_found:
            logger.error(f'{self._class_name}:: not found season episodes :: {not_found}')
            raise NotFound(f"{self._class_name}:: matching names :: {not_found}")

        logger.info(f'{self._class_name}:: found')
        return season

    def fill_episode_name(self, file: Episode) -> Episode:
        """
        Retrieves the episode name for the given file.
        :param file: to fill episode name
        :return: Returns the file with the new episode name
        """

        logger.info(f'{self._class_name}:: searching for episode :: {self.build_search_keyword(file)}')

        page = self.__load_page(file)
        episode_name = page.episode_name(file.season, file.episode)
        if episode_name is None:
            raise NotFound(f"{self._class_name}:: matching names :: {[file]}")

        file.metadata.episode_name = episode_name

        logger.info(f'{self._class_name}:: found match')
        return file

    @staticmethod
    def build_search_keyword(item) -> str:
        keyword = item.media_name
        season = Parser.season_text(keyword)
        if season is not None:
            keyword = keyword.split(season)[0]
        return generic_clean(keyword).replace(' ', '_')

    def __load_page(self, item) -> WikipediaPage:
        page = WikipediaEpisodePage(self.build_search_keyword(item))
        if not page.is_valid:
            page = WikipediaMainPage(self.build_search_keyword(item))
        if not page.is_valid:
            raise NotFound(f"{self._class_name}:: matching page for :: {self.build_search_keyword(item)}")
        return page
