import logging
import re
from typing import Optional

from bs4 import Tag

from src.datasources.scrapper.wikipedia.pages._page import WikipediaPage

logger = logging.getLogger()


class WikipediaMainPage(WikipediaPage):
    BASE_URL = 'https://en.wikipedia.org/wiki/{}#Episode_list'

    def title(self) -> str:
        return self._soup.find('h1', {'id': 'firstHeading'}).text

    @staticmethod
    def check_url(url: str) -> bool:
        return re.match(r'.*#Episode_list', url, re.IGNORECASE) is not None

    def season_name(self, season: int) -> Optional[str]:
        # Usually main page only contains the episode names for animes with only one season
        return None

    def _retrieve_season_table(self, season: int) -> Tag:
        return self._soup.find_all('table', {'class': 'wikitable plainrowheaders wikiepisodetable'})[season - 1]
