import json
import logging
from pprint import pformat
from typing import List
from typing import Optional

import requests
from requests import RequestException

from src import settings
from src.core.models.config import GlobalConfig
from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.core.types import Language
from src.filemapper.datasources.datasource import AnimeAPI
from src.filemapper.datasources.exceptions import InvalidConfiguration
from src.filemapper.datasources.models import MalData

logger = logging.getLogger()


# https://myanimelist.net/apiconfig/references/api/v2
class MalAPI(AnimeAPI):
    DATASOURCE = DatasourceName.MAL
    BASE_URL = 'https://api.myanimelist.net/v2/anime?q={anime}&fields=alternative_titles'
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
        logger.info(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            # data format: [{'node': {'id': int, 'alternative_titles': {'en': '', 'ja': ''}, 'title': 'str'}}]
            content = json.loads(response.content)['data']
            if settings.LOG_HTTP:
                logger.debug(f'{self._class}: {pformat(content)}')

            if not content:
                logger.error(f'{self._class}:: no match')
                return None

            # parse data into Python objects
            data: List[MalData] = [MalData(d['node']) for d in content]
            match = self._best_match(keyword, lang, data, season, season_name)

            logger.info(f'{self._class}:: matching result :: {match}')
            return AnimeMetadata(
                datasource_data=(self.DATASOURCE, match),
                title=match.title(Language.JA),
                title_lang=match.title_lang,
            )

        raise RequestException(response=response)

    def __get_url(self, keyword: str) -> str:
        return GlobalConfig().mal_url if GlobalConfig().mal_url else self.BASE_URL.format(anime=keyword)
