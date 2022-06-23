import logging
import re
from typing import Optional

from bs4 import Tag

from src.datasources.scrapper.wikipedia.pages._page import WikipediaPage

logger = logging.getLogger()


class WikipediaEpisodePage(WikipediaPage):
    BASE_URL = 'https://en.wikipedia.org/wiki/List_of_{}_episodes'

    def season_name(self, season: int) -> Optional[str]:
        if self.__has_toc():
            season_re = re.compile(f'Season {season}.*')
            try:
                # Try to find TOC as Season X
                return self.soup.find_all("span", {"class": "toctext"}, text=season_re)[0].string
            except IndexError:
                episode_list_re = re.compile('Episode list', re.IGNORECASE)
                seasons_li = self.soup.find_all("span", {'class': 'toctext'}, text=episode_list_re)[0].parent.parent
                season_spans = seasons_li.find('ul').find_all("span", {"class": "toctext"})
                # Some TOCs have OVA seasons between normal seasons...
                return [s for s in season_spans if 'ova' not in s.text.lower()][season - 1].text
        return None

    def _retrieve_season_table(self, season: int) -> Tag:
        if self.__has_toc():
            season_name = self.season_name(season)
            season_header = self.soup.find("span", {"id": season_name.replace(' ', '_')})
            return season_header.find_next('table')
        else:
            return self.soup.find_all("table", {"class": "wikitable plainrowheaders wikiepisodetable"})[season - 1]

    def __has_toc(self) -> bool:
        return self.soup.find('div', {'id': 'toc'}) is not None
