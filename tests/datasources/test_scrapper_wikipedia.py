import re
import unittest
from unittest import mock

import responses

from src.core.models import MediaItem
from src.core.models.metadata import AnimeMetadata
from src.datasources.scrapper import WikipediaScrapper
from src.parsers import Parser
from src.matchers import MediaType
from tests.factories import MediaItemFactory
from tests.test import CommonTest


class TestWikipediaScrapper(CommonTest):

    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)

    def setUp(self) -> None:
        super(TestWikipediaScrapper, self).setUp()
        self.responses = responses.RequestsMock()
        self.responses.start()

        self.file = MediaItemFactory()

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_episode_page(self, mock_parser):
        data = self._load_page('wikipedia_episode_page_great_pretender.html')
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 1
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_episode_name(self.file)

        metadata = self.file.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'CASE1_1: Los Angeles Connection')

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_main_page(self, mock_parser):
        data = self._load_page('wikipedia_main_page_ahiru_no_sora.html')
        self.responses.add(responses.GET, url=re.compile('.*'), status=404)
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 2
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_episode_name(self.file)

        metadata = self.file.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'Boys Without Talent')

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_episode_page_2(self, mock_parser):
        data = self._load_page('wikipedia_episode_page_seikon_no_qwaser.html')
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 2
        mock_parser.season.return_value = 2

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_episode_name(self.file)

        metadata = self.file.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'The Location of the Magdalene')

    def __wikipedia_search_keyword(self, item: MediaItem, lang: str = None) -> str:
        return self.parser.media_name(item).replace(' ', '_')


if __name__ == '__main__':
    unittest.main()
