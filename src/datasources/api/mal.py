import json
import logging
from pprint import pformat
from typing import List, Tuple

import requests
from requests import RequestException

import settings
from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.datasources.datasource import API
from src.datasources.exceptions import InvalidConfiguration
from src.parsers import Parser

logger = logging.getLogger()


# https://myanimelist.net/apiconfig/references/api/v2
class MalAPI(API[int, AnimeMetadata]):
    DATASOURCE = DatasourceName.MAL
    BASE_URL = 'https://api.myanimelist.net/v2'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'X-MAL-CLIENT-ID': settings.MAL_CLIENT_ID,
    }

    def __init__(self, parser: Parser):
        super(MalAPI, self).__init__(parser)
        if settings.MAL_CLIENT_ID is None:
            raise InvalidConfiguration('MAL_CLIENT_ID')

    def search_anime(self, keyword: str) -> List[Tuple[str, int]]:
        """
        Find the closest parsers anime from MAL searching using 'keyword'
        :param keyword: used to search
        :return: anime matches
        """
        url = f'{self.BASE_URL}/anime?q={keyword}'
        response = requests.get(url, headers=self.HEADERS)
        logger.info(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            # data format: [{'node': {'id': int, 'main_picture': {'large': 'str', 'medium': 'str'}, 'title': 'str'}}]
            data = json.loads(response.content)['data']
            if settings.LOG_HTTP:
                logger.debug(f'{self._class}: {pformat(data)}')
            found = [(r['node']['title'], r['node']['id']) for r in data]
            logger.info(f'{self._class}:: closest result :: {found}')
            return found

        raise RequestException(response=response)

    def get_anime_details(self, anime_id: int) -> AnimeMetadata:
        """
        Get the MAL anime details using 'anime_id'
        :param anime_id: used to retrieve the details
        :return: the retrieved MAL data
        """
        url = f'{self.BASE_URL}/anime/{anime_id}?fields=id,title,alternative_titles,media_type'
        response = requests.get(url, headers=self.HEADERS)
        logger.info(f'{self._class}:: details for :: {url}')

        if response.status_code == 200:
            # data format: {'alternative_titles': {'en': '', 'ja': ''}, 'id': int, 'media_type': 'tv', 'title': 'str'}
            data = json.loads(response.content)
            logger.info(f'{self._class}:: found details :: {pformat(data)}')
            return AnimeMetadata(
                datasource_id=data['id'],
                datasource=self.DATASOURCE,
                title=data['title'],
                alternative_titles=data['alternative_titles']
            )

        raise RequestException(response=response)
