import logging

from bs4 import Tag

from src.datasources.scrapper.wikipedia.pages._page import WikipediaPage

logger = logging.getLogger()


class WikipediaMainPage(WikipediaPage):
    BASE_URL = 'https://en.wikipedia.org/wiki/{}#Episode_list'

    def _retrieve_season_table(self, season: int) -> Tag:
        return self.soup.find_all("table", {"class": "wikitable plainrowheaders wikiepisodetable"})[season - 1]
