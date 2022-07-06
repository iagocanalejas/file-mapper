import json
import logging
from pprint import pformat
from typing import Tuple, List

import requests
from requests import RequestException

import settings
from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.datasources.datasource import API

logger = logging.getLogger()


# https://anilist.gitbook.io/anilist-apiv2-docs/
class AnilistAPI(API[int, AnimeMetadata]):
    DATASOURCE = DatasourceName.ANILIST
    BASE_URL = 'https://graphql.anilist.co'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    }

    ANIME_INFO_QUERY = """\
        query ($id: Int) {
            Media(id: $id, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
            }
        }"""
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
                    }
                }
            }
        }"""

    def search_anime(self, keyword: str) -> List[Tuple[str, int]]:
        """
        Find top ANILIST matches using 'keyword'
        :return: tuple containing ANILIST romaji name and ANILIST id
        """
        variables = {'query': keyword}
        response = requests.post(
            self.BASE_URL,
            headers={},
            json={'query': self.ANIME_SEARCH_QUERY, 'variables': variables}
        )
        logger.info(f'{self._class}:: searching for :: {keyword}')

        if response.status_code == 200:
            # data format: [{'id': int, 'title': {'romaji': str}}
            data = json.loads(response.content)['data']['Page']['media']
            if settings.LOG_HTTP:
                logger.debug(f'{self._class}: {pformat(data)}')
            found = [(r['title']['romaji'], r['id']) for r in data]
            logger.info(f'{self._class}:: found results :: {found}')
            return found

        raise RequestException(response=response)

    def get_anime_details(self, anime_id: int) -> AnimeMetadata:
        """
        Get the ANILIST anime details using 'anime_id'
        :return: ANILIST data parsed into AnimeMetadata
        """
        variables = {'id': anime_id}
        response = requests.post(
            self.BASE_URL,
            headers={},
            json={'query': self.ANIME_INFO_QUERY, 'variables': variables}
        )
        logger.info(f'{self._class}:: details for :: {anime_id}')

        if response.status_code == 200:
            # data format: [{'id': int, 'title': {'romaji': str, 'english': str}}]
            data = json.loads(response.content)['data']['Media']
            logger.info(f'{self._class}:: found details :: {pformat(data)}')

            return AnimeMetadata(
                datasource_id=anime_id,
                datasource=self.DATASOURCE,
                title=data['title']['romaji'],
                alternative_titles={'en': data['title']['english']}
            )

        raise RequestException(response=response)
