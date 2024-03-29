import logging
import re
from abc import ABC
from abc import abstractmethod
from http.client import NOT_FOUND
from typing import List
from typing import Optional
from typing import Tuple

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4 import Tag

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

    def __init__(self, keyword: str = None, url: str = None):
        self._keyword = keyword
        self._url = url
        self._soup = None

    def __str__(self):
        return self.url

    @property
    def url(self) -> str:
        return self._url if self._url else self.BASE_URL.format(self._keyword)

    @property
    def is_valid(self) -> bool:
        re_el = re.compile('episode.list', re.IGNORECASE)
        return (
                self._soup is not None
                and (
                        self._soup.find('span', {'id': 'Episode_list'}, recursive=True) is not None
                        or self._soup.find('span', string=re_el, recursive=True) is not None
                )
        )

    def episode_name(self, season: int, episode: int, episode_part: Optional[int] = None) -> Optional[str]:
        season_table = self._retrieve_season_table(season)
        episode_name = self._retrieve_episode_name(season_table, episode, episode_part)

        if episode_name is not None:
            logger.debug(f'{self._class}:: found :: {episode_name}')
            return episode_name

        logger.debug(f'{self._class}:: not found episode name')

    @staticmethod
    @abstractmethod
    def check_url(url: str) -> bool:
        pass

    @abstractmethod
    def title(self) -> str:
        pass

    @abstractmethod
    def season_name(self, season: int) -> Optional[str]:
        pass

    @abstractmethod
    def _retrieve_season_table(self, season: int) -> Tag:
        pass

    def _retrieve_episode_name(
            self, season_table: Tag, episode: int, episode_part: Optional[int] = None
    ) -> Optional[str]:
        episode = f'{episode}' if episode_part is None else f'{episode}.{episode_part}'
        header, rows = self.__retrieve_table_header_rows(season_table)

        # filter only episode rows
        rows = [r for r in rows if r.get('class') is not None and 'vevent' in r.get('class')]

        for row in rows:
            columns = row.find_all('th') + row.find_all('td')  # fists column is a th
            if columns[1].text == episode or columns[0].text == episode:
                logger.debug(f'{self._class}:: episode row :: {row}')
                episode_name = columns[2].text if self.__has_season_episode_no(header) else columns[1].text
                return re.search(r'\"(.*?)\"', episode_name).group(1)

    @staticmethod
    def __retrieve_table_header_rows(season_table: Tag) -> Tuple[Tag, List[Tag]]:
        if season_table.find('thead') is not None:
            return season_table.find('thead').find('tr'), season_table.find('tbody').find_all('tr')
        rows = season_table.find_all('tr')
        return rows[0], rows[1:]

    @staticmethod
    def __has_season_episode_no(header: Tag) -> bool:
        columns = header.find_all('th') + header.find_all('td')
        return (
                any(re.match(r'No.*season', column.text, re.IGNORECASE) for column in columns) or
                any(re.match(r'No.*part', column.text, re.IGNORECASE) for column in columns)
        )

    async def load(self, session: ClientSession) -> 'WikipediaPage':
        logger.debug(f'{self._class}:: loading page :: {self}')

        response = await session.get(self.url, headers=self.HEADERS)
        if response.status == NOT_FOUND:
            return self

        content = await response.read()
        self._soup = BeautifulSoup(content, 'html5lib')

        return self
