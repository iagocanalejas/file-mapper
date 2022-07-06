import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

import settings
from src.core.types import Object

logger = logging.getLogger()


class WikipediaPage(ABC, Object):
    BASE_URL: str
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    def __init__(self, keyword: str):
        self.keyword = keyword

        self.soup = self.__load_soup()

    @property
    def url(self):
        return self.BASE_URL.format(self.keyword)

    @property
    def is_valid(self) -> bool:
        re_el = re.compile('episode.list', re.IGNORECASE)
        return (
                self.soup is not None
                and (
                    self.soup.find('span', {'id': 'Episode_list'}, recursive=True) is not None
                    or self.soup.find('span', string=re_el, recursive=True) is not None
                )
        )

    def episode_name(self, season: int, episode: int) -> Optional[str]:
        season_table = self._retrieve_season_table(season)
        episode_name = self._retrieve_episode_name(season_table, episode)

        if episode_name is not None:
            logger.debug(f'{self._class}:: found :: {episode_name}')
            return episode_name

        logger.info(f'{self._class}:: not found episode name')
        return None

    @abstractmethod
    def season_name(self, season: int) -> Optional[str]:
        pass

    @abstractmethod
    def _retrieve_season_table(self, season: int) -> Tag:
        pass

    def _retrieve_episode_name(self, season_table: Tag, episode: int) -> Optional[str]:
        if len(season_table.find_all("td", {"class": "description"}, recursive=True)) > 0:
            episode_row = season_table.findChildren(['tr'])[(episode * 2) - 1]
            episode_row_data = episode_row.find("td", {"class": "summary"}).text
        else:
            episode_row = season_table.find_all('tr', {"class": "vevent"})[episode - 1]
            episode_row_data = episode_row.find("td", {"class": "summary"}).text

        logger.debug(f'{self._class}:: episode row :: {episode_row_data}')
        return re.search(r'\"(.*?)\"', episode_row_data).group(1)

    def __load_soup(self) -> Optional[BeautifulSoup]:
        logger.info(f'{self._class}:: trying :: {self.url}')

        response = requests.get(self.url, headers=self.HEADERS)
        if response.status_code == 404:
            return None

        soup = BeautifulSoup(response.content, 'html5lib')

        if settings.LOG_HTTP:
            logger.debug(f'{self._class}: {soup.prettify()}')

        return soup
