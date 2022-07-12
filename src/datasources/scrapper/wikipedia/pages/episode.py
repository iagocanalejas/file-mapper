import logging
import re
from typing import Optional

from bs4 import Tag

from src.datasources.scrapper.wikipedia.pages._page import WikipediaPage

logger = logging.getLogger()


class WikipediaEpisodePage(WikipediaPage):
    BASE_URL = 'https://en.wikipedia.org/wiki/List_of_{}_episodes'

    def title(self) -> str:
        title = self.soup.find('h1', {'id': 'firstHeading'}).text
        return title.replace('List of', '').replace('episodes', '').strip()

    def season_name(self, season: int) -> Optional[str]:
        if self.__has_toc():
            season_re = re.compile(f'Season {season}.*')
            try:
                # Try to find TOC as Season X
                return self.soup.find_all("span", {"class": "toctext"}, text=season_re)[0].string
            except IndexError:
                episode_list_re = re.compile('Episode list', re.IGNORECASE)
                season_li = self.soup.find_all("span", {'class': 'toctext'}, text=episode_list_re)[0].parent.parent
                season_ul = season_li.find('ul')
                if season_ul is not None:
                    season_spans = season_ul.find_all("span", {"class": "toctext"})
                    # Some TOCs have OVA seasons between normal seasons...
                    return [s for s in season_spans if not re.search(r'ova', s.text, re.IGNORECASE)][season - 1].text
        return None

    def _retrieve_season_table(self, season: int) -> Tag:
        if self.__has_toc():
            season_name = self.season_name(season)
            if season_name is not None:
                season_header = self.soup.find("span", {"id": season_name.replace(' ', '_')})
                return season_header.find_next('table')
        return self.soup.find_all("table", {"class": "wikitable plainrowheaders wikiepisodetable"})[season - 1]

    def __has_toc(self) -> bool:
        return self.soup.find('div', {'id': 'toc'}) is not None

    def __patch_season_name(self, season_name: str) -> str:
        match = re.match(self.title(), season_name, re.IGNORECASE)
        if match is not None:
            return season_name.replace(match.group(0), '').strip()
        return season_name
