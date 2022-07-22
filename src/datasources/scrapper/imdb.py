import logging
from typing import Callable
from typing import List
from typing import Tuple

import requests
from bs4 import BeautifulSoup

from src import settings
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.models.metadata import as_anime
from src.core.types import DatasourceName
from src.datasources.api import ImdbAPI
from src.datasources.datasource import AnimeDatasource
from src.datasources.datasource import Scrapper
from src.datasources.exceptions import NotFound
from src.parsers import Parser

logger = logging.getLogger()


class ImdbScrapper(Scrapper, AnimeDatasource):
    DATASOURCE = DatasourceName.IMDB_SCRAPPER
    BASE_URL = 'https://www.imdb.com/title/{anime_id}/episodes?season={season}'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    def __init__(self, parser: Parser, format_fn: Callable[[MediaItem], str], **kwargs):
        super().__init__(parser, **kwargs)
        self.format_fn = format_fn

    @property
    def is_valid(self) -> bool:
        return (
                self.soup is not None
                and self.soup.find('div', {'id': 'episodes_content'}) is not None
                and self.soup.find('div', {'id': 'episodes_content'}).find_all('a', {'itemprop': 'name'})
        )

    def fill_show_names(self, show: Show) -> Show:
        for season in show.seasons:
            self.fill_season_names(season)
        for episode in show.episodes:
            self.fill_episode_name(episode)

        return show

    def fill_season_names(self, season: Season) -> Season:
        page = self.__load_page(season, season=self.parser.season(season))
        self.__fill_episodes(page, season.episodes)
        self.__fill_season(page, season)

        return season

    def fill_episode_name(self, episode: Episode) -> Episode:
        page = self.__load_page(episode, season=self.parser.season(episode))
        self.__fill_episodes(page, [episode])

        return episode

    def __retrieve_anime_id(self, item: MediaItem) -> str:
        # try to find IMDB anime ID in the existing metadata
        data = as_anime(item.metadata).datasource_data[ImdbAPI.DATASOURCE]
        if data is not None:
            return data.id

        # use IMDB API to find the IMDB anime ID
        season = self.parser.season(item) if not isinstance(item, Show) else 1
        season_name = self.parser.season_name(item) if not isinstance(item, Show) else None
        return ImdbAPI(parser=self.parser).search_anime(
            keyword=self.format_fn(item),
            lang=item.language,
            season=season,
            season_name=season_name,
        ).datasource_data[1].id

    def __load_page(self, item: MediaItem, season: int) -> BeautifulSoup:
        url = self.BASE_URL.format(
            anime_id=self.__retrieve_anime_id(item),
            season=season,
        )

        response = requests.get(url, headers=self.HEADERS)
        logger.info(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            self.soup = BeautifulSoup(response.content, 'html5lib')

        if self.is_valid:
            if settings.LOG_HTTP:
                logger.debug(f'{self._class}: {self.soup.prettify()}')
            return self.soup

        raise NotFound(f'{self._class}:: matching page for :: {item}')

    def __fill_episodes(self, page: BeautifulSoup, episodes: List[Episode]):
        not_found = []
        episode_divs = [i.text for i in page.find_all('a', {'itemprop': 'name'})]

        for episode in episodes:
            episode_no = self.parser.episode(episode)
            if episode_no >= len(episode_divs):
                not_found.append(episode)
                continue

            episode_name = episode_divs[episode_no - 1]
            if episode_name is None:
                not_found.append(episode)
                continue

            episode.metadata.episode_name = episode_name

        logger.info(f'{self._class}:: NOT FOUND :: episode names :: {[s.item_name for s in not_found]}')

    def __fill_season(self, page: BeautifulSoup, season: Season):
        season_name = page.find('div', {'id': 'episodes_content'}).find('h3', {'itemprop': 'name'}).text

        if season_name is None:
            logger.info(f'{self._class}:: NOT FOUND :: season names :: {season.item_name}')

        season.metadata.season_name = season_name.replace('\xa0', ' ')
