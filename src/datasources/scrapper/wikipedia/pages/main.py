import logging
from typing import Optional

from bs4 import Tag

from src.datasources.scrapper.wikipedia.pages._page import WikipediaPage

logger = logging.getLogger()


class WikipediaMainPage(WikipediaPage):
    BASE_URL = 'https://en.wikipedia.org/wiki/{}#Episode_list'

    def title(self) -> Optional[str]:
        return self.soup.find('h1', {'id': 'firstHeading'}).text

    def season_name(self, season: int) -> Optional[str]:
        # Usually main page only contains the episode names for animes with only one season
        return None

    def _retrieve_season_table(self, season: int) -> Tag:
        return self.soup.find_all("table", {"class": "wikitable plainrowheaders wikiepisodetable"})[season - 1]
