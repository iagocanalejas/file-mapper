import json
import logging
from dataclasses import dataclass
from pprint import pformat
from typing import Dict
from typing import List
from typing import Optional

import requests
from requests import RequestException

from src import settings
from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.core.types import Language
from src.datasources.datasource import AnimeAPI
from src.datasources.datasource import APIData

logger = logging.getLogger()


# https://imdb-api.com/
class ImdbAPI(AnimeAPI):
    DATASOURCE = DatasourceName.IMDB
    BASE_URL = 'https://imdb-api.com/{lang}/API/Search/{api_key}/{search_expression}'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    }

    def search_anime(self, keyword: str, lang: Language, season: int, season_name: str) -> Optional[AnimeMetadata]:
        url = self.BASE_URL.format(
            lang=lang.value,
            api_key=settings.IMDB_API_KEY,
            search_expression=keyword,
        )
        response = requests.get(url, headers=self.HEADERS)
        logger.info(f'{self._class}:: searching for :: {url}')

        if response.status_code == 200:
            content = json.loads(response.content)['results']
            if settings.LOG_HTTP:
                logger.debug(f'{self._class}: {pformat(content)}')

            if not content:
                return None

            # parse data into Python objects
            data: List[_ImdbData] = [_ImdbData(d) for d in content]
            match = self._best_match(keyword, lang, data, season, season_name)

            logger.info(f'{self._class}:: matching result :: {match}')
            return AnimeMetadata(
                datasource_data={self.DATASOURCE: match.id},
                title=match.title(Language.JA),
                title_lang=match.title_lang,
                alternative_titles=match.alternative_titles,
            )

        raise RequestException(response=response)


@dataclass
class _ImdbData(APIData):
    title_lang = Language.EN

    def __init__(self, d: Dict):
        super().__init__(d)
        self._title = d['title']
        self.alternative_titles = {Language.EN.value: d['title']}
