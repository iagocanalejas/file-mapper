import json
import logging
from dataclasses import dataclass
from pprint import pformat
from typing import Dict
from typing import List

import requests
from requests import RequestException

from src import settings
from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.datasources.datasource import AnimeAPI
from src.datasources.datasource import APIData
from src.datasources.exceptions import InvalidConfiguration
from src.parsers import Parser

logger = logging.getLogger()


# https://myanimelist.net/apiconfig/references/api/v2
class MalAPI(AnimeAPI):
    DATASOURCE = DatasourceName.MAL
    BASE_URL = 'https://api.myanimelist.net/v2'
    EXTRA_FIELDS = 'alternative_titles'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'X-MAL-CLIENT-ID': settings.MAL_CLIENT_ID,
    }

    def __init__(self, parser: Parser):
        super().__init__(parser)
        if settings.MAL_CLIENT_ID is None:
            raise InvalidConfiguration('MAL_CLIENT_ID')

    def search_anime(self, keyword: str, season: int, season_name: str) -> AnimeMetadata:
        url = f'{self.BASE_URL}/anime?q={keyword}&fields={self.EXTRA_FIELDS}'
        response = requests.get(url, headers=self.HEADERS)
        logger.info(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            # data format: [{'node': {'id': int, 'alternative_titles': {'en': '', 'ja': ''}, 'title': 'str'}}]
            content = json.loads(response.content)['data']
            if settings.LOG_HTTP:
                logger.debug(f'{self._class}: {pformat(content)}')

            # parse data into Python objects
            data: List[_MalData] = [_MalData(d['node']) for d in content]
            match = self._best_match(keyword, data, season, season_name)

            logger.info(f'{self._class}:: matching result :: {match}')
            return AnimeMetadata(
                datasource_id=match.id,
                datasource=self.DATASOURCE,
                title=match.title('ja'),
                alternative_titles=match.alternative_titles,
            )

        raise RequestException(response=response)


@dataclass
class _MalData(APIData):
    def __init__(self, d: Dict):
        super().__init__(d)
        self._title = d['title']
        self.alternative_titles = d['alternative_titles']
