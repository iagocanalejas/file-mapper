import logging
from typing import Tuple, List

from AnilistPython import Anilist

from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.datasources.datasource import API
from src.parsers import Parser

logger = logging.getLogger()


# TODO: refactor to directly use the API instead of the library
# https://github.com/ReZeroE/AnilistPython/wiki/Anime
class AnilistAPI(API[int, AnimeMetadata]):
    DATASOURCE = DatasourceName.ANILIST

    def __init__(self, parser: Parser):
        super(AnilistAPI, self).__init__(parser)
        self._anilist = Anilist()

    def __find_anime_id(self, keyword: str) -> int:
        return self._anilist.get_anime_id(keyword)

    def search_anime(self, keyword: str) -> List[Tuple[str, int]]:
        logger.info(f'{self._class}:: searching for :: {keyword}')
        found_anime = self._anilist.get_anime(keyword)
        anime_id = self.__find_anime_id(found_anime['name_romaji'])
        logger.info(f'{self._class}:: retrieved :: {found_anime}')
        logger.info(f'{self._class}:: with id :: {anime_id}')
        return [(found_anime['name_romaji'], anime_id)]

    def get_anime_details(self, anime_id: int) -> AnimeMetadata:
        anime_dict = self._anilist.get_anime_with_id(anime_id)
        logger.info(f'{self._class}:: found details :: {anime_dict}')

        return AnimeMetadata(
            datasource_id=anime_id,
            datasource=self.DATASOURCE,
            title=anime_dict['name_romaji'],
            alternative_titles={'en': anime_dict['name_english']}
        )
