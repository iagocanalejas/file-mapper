import json
import logging
from pprint import pformat
from typing import Any, List

import requests
from requests import RequestException

import settings
from src.datasources._datasource import API
from src.datasources.exceptions import InvalidConfiguration
from src.models.metadata import AnimeMetadata
from src.utils.strings import levenshtein_distance

logger = logging.getLogger()


# https://myanimelist.net/apiconfig/references/api/v2
class MalAPI(API):
    BASE_URL = 'https://api.myanimelist.net/v2'
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'X-MAL-CLIENT-ID': settings.MAL_CLIENT_ID,
    }

    def __init__(self):
        super(MalAPI, self).__init__()
        if settings.MAL_CLIENT_ID is None:
            raise InvalidConfiguration('MAL_CLIENT_ID')

    def find_anime(self, keyword: str) -> int:
        """
        Find the closest parsers anime from MAL searching using 'keyword'
        :param keyword: used to search
        :return: the closest parsers anime ID
        """
        url = f'{self.BASE_URL}/anime?q={keyword}'
        response = requests.get(url, headers=self.HEADERS)
        logger.info(f'{self._class_name}:: searching for :: {url}')

        if response.status_code == 200:
            # data format: [{'node': {'id': int, 'main_picture': {'large': 'str', 'medium': 'str'}, 'title': 'str'}}]
            data = json.loads(response.content)['data']
            if settings.LOG_HTTP:
                logger.debug(f'{self._class_name}: {pformat(data)}')
            closest_result = self.__get_closest_result(keyword, data)
            logger.info(f'{self._class_name}:: closest result :: {pformat(closest_result)}')
            return closest_result['node']['id']

        raise RequestException(response=response)

    def get_anime_details(self, anime_id: int) -> AnimeMetadata:
        """
        Get the MAL anime details using 'anime_id'
        :param anime_id: used to retrieve the details
        :return: the retrieved MAL data
        """
        url = f'{self.BASE_URL}/anime/{anime_id}?fields=id,title,alternative_titles,media_type'
        response = requests.get(url, headers=self.HEADERS)

        if response.status_code == 200:
            # data format: {'alternative_titles': {'en': '', 'ja': ''}, 'id': int, 'media_type': 'tv', 'title': 'str'}
            data = json.loads(response.content)
            logger.info(f'{self._class_name}:: found details :: {pformat(data)}')
            return AnimeMetadata(
                mal_id=data['id'],
                title=data['title'],
                media_type=data['media_type'],
                alternative_titles=data['alternative_titles']
            )

        raise RequestException(response=response)

    @staticmethod
    def build_search_keyword(item) -> str:
        season = item.season if hasattr(item, 'season') else 0
        return f'{item.media_name} Season {season}' if season > 1 else f'{item.media_name}'

    @staticmethod
    def __get_closest_result(keyword: str, elements: List[Any]) -> Any:
        best_distance = levenshtein_distance(keyword, elements[0]['node']['title'])
        best_word = elements[0]
        for w in elements:
            d = levenshtein_distance(keyword, w['node']['title'])
            if d < best_distance:
                best_distance = d
                best_word = w

        return best_word
