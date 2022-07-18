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
from src.core.types import Language
from src.datasources.datasource import AnimeAPI
from src.datasources.datasource import APIData

logger = logging.getLogger()


# https://anilist.gitbook.io/anilist-apiv2-docs/
class AnilistAPI(AnimeAPI):
    DATASOURCE = DatasourceName.ANILIST
    BASE_URL = 'https://graphql.anilist.co'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    }
    ANIME_SEARCH_QUERY = """\
        query ($query: String) {
            Page (page: 1, perPage: 10) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                }
                media (search: $query, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                    }
                }
            }
        }"""

    def search_anime(self, keyword: str, lang: Language, season: int, season_name: str) -> AnimeMetadata:
        variables = {'query': keyword}
        response = requests.post(
            self.BASE_URL,
            headers={},
            json={'query': self.ANIME_SEARCH_QUERY, 'variables': variables}
        )
        logger.info(f'{self._class}:: searching for :: {keyword}')

        if response.status_code == 200:
            # data format: [{'id': int, 'title': {'romaji': str, 'english': str}}
            content = json.loads(response.content)['data']['Page']['media']
            if settings.LOG_HTTP:
                logger.debug(f'{self._class}: {pformat(content)}')

            # parse data into Python objects
            data: List[_AnilistData] = [_AnilistData(d) for d in content]
            match = self._best_match(keyword, lang, data, season, season_name)

            logger.info(f'{self._class}:: matching result :: {match}')
            return AnimeMetadata(
                datasource_id=match.id,
                datasource=self.DATASOURCE,
                title=match.title(Language.JA),
                alternative_titles=match.alternative_titles
            )

        raise RequestException(response=response)


@dataclass
class _AnilistData(APIData):
    def __init__(self, d: Dict):
        super().__init__(d)
        self._title = d['title']['romaji']
        self.alternative_titles = {'ja': d['title']['romaji'], 'en': d['title']['english']}
