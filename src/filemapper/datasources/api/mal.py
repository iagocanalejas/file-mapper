import json
import logging
from typing import List
from typing import Optional

import requests
from requests import RequestException

from src import runner
from src import settings
from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.core.types import Language
from src.filemapper.datasources.datasource import AnimeAPI
from src.filemapper.datasources.exceptions import InvalidConfiguration
from src.filemapper.datasources.exceptions import NotFound
from src.filemapper.datasources.models import MalData

logger = logging.getLogger()


# https://myanimelist.net/apiconfig/references/api/v2
class MalAPI(AnimeAPI):
    DATASOURCE = DatasourceName.MAL
    BASE_URL = 'https://api.myanimelist.net/v2/anime?q={anime}&fields=alternative_titles'
    BY_ID_URL = 'https://api.myanimelist.net/v2/anime/{anime_id}?fields=alternative_titles'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'X-MAL-CLIENT-ID': settings.MAL_CLIENT_ID,
    }

    def __init__(self):
        super().__init__()
        if settings.MAL_CLIENT_ID is None:
            raise InvalidConfiguration('MAL_CLIENT_ID')

    def search_anime(self, keyword: str, lang: Language, season: int, season_name: str) -> Optional[AnimeMetadata]:
        url = self.__get_url(keyword)
        response = requests.get(url, headers=self.HEADERS)
        logger.debug(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            # data format: [{'node': {'id': int, 'alternative_titles': {'en': '', 'ja': ''}, 'title': 'str'}}]
            content = json.loads(response.content)['data']

            if not content:
                logger.error(f'{self._class}:: no match')
                return None

            # parse data into Python objects
            data: List[MalData] = [MalData(d['node']) for d in content]
            match = self._best_match(keyword, lang, data, season, season_name)

            logger.debug(f'{self._class}:: matching result :: {match}')
            return AnimeMetadata(
                datasource_data=(self.DATASOURCE, match),
                title=match.title(Language.JA),
                title_lang=match.title_lang,
            )

        raise RequestException(response=response)

    def options(self, url: str) -> List[AnimeMetadata]:
        response = requests.get(url, headers=self.HEADERS)
        logger.debug(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            # data format: [{'node': {'id': int, 'alternative_titles': {'en': '', 'ja': ''}, 'title': 'str'}}]
            content = json.loads(response.content)['data']

            if not content:
                logger.error(f'{self._class}:: no options found')
                return []

            # parse data into Python objects
            data: List[MalData] = [MalData(d['node']) for d in content]
            logger.debug(f'{self._class}:: options found :: {data}')
            return [
                AnimeMetadata(
                    datasource_data=(self.DATASOURCE, option),
                    title=option.title(Language.JA),
                    title_lang=option.title_lang,
                ) for option in data
            ]

        raise RequestException(response=response)

    def anime_by_id(self, mal_id: str) -> AnimeMetadata:
        url = self.BY_ID_URL.format(anime_id=mal_id)
        response = requests.get(url, headers=self.HEADERS)
        logger.debug(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            # data format: {'id': int, 'alternative_titles': {'en': '', 'ja': ''}, 'title': 'str'}
            content = json.loads(response.content)

            if not content:
                logger.error(f'{self._class}:: no anime found {mal_id}')
                raise NotFound(f'anime with id: {mal_id}')

            # parse data into Python objects
            data: MalData = MalData(content)
            logger.debug(f'{self._class}:: anime found :: {data}')
            return AnimeMetadata(
                datasource_data=(self.DATASOURCE, data),
                title=data.title(Language.JA),
                title_lang=data.title_lang,
            )

        raise RequestException(response=response)

    def __get_url(self, keyword: str) -> str:
        return runner.mal_url if runner.mal_url else self.BASE_URL.format(anime=keyword)
