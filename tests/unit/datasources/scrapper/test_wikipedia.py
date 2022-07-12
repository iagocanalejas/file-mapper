import os
import re
import unittest
from unittest import mock

import responses

from src.core.models import MediaItem
from src.core.models.metadata import AnimeMetadata
from src.datasources.scrapper import WikipediaScrapper
from src.matchers import MediaType
from src.parsers import Parser
from tests import settings
from tests.factories import AnimeMetadataFactory, EpisodeFactory, SeasonFactory
from tests.utils import load_page


class TestWikipediaScrapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)

    def setUp(self) -> None:
        super(TestWikipediaScrapper, self).setUp()
        self.responses = responses.RequestsMock()
        self.responses.start()

        self.episode = EpisodeFactory.create(item_name='', _metadata=AnimeMetadataFactory())
        self.season = SeasonFactory.create(item_name='', episodes=[], _metadata=AnimeMetadataFactory())

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_episode_page(self, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_great_pretender.html'))
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 1
        mock_parser.episode_part.return_value = None
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'CASE1_1: Los Angeles Connection')

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_main_page(self, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'main_page_ahiru_no_sora.html'))
        self.responses.add(responses.GET, url=re.compile('.*'), status=404)
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 2
        mock_parser.episode_part.return_value = None
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'Boys Without Talent')

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_episode_page_2(self, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_seikon_no_qwaser.html'))
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 2
        mock_parser.episode_part.return_value = None
        mock_parser.season.return_value = 2

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'The Location of the Magdalene')

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_season_from_episode_page_as_season_x(self, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_hajime_no_ippo.html'))
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 1
        mock_parser.episode_part.return_value = None
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_season_names(self.season)

        metadata = self.season.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.season_name, 'Season 1: The Fighting!')

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_season_from_episode_page_as_name(self, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_seikon_no_qwaser.html'))
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        mock_parser.episode.return_value = 1
        mock_parser.episode_part.return_value = None
        mock_parser.season.return_value = 2

        WikipediaScrapper(mock_parser, self.__wikipedia_search_keyword).fill_season_names(self.season)

        metadata = self.season.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.season_name, 'II')

    def __wikipedia_search_keyword(self, item: MediaItem, lang: str = None) -> str:
        return self.parser.media_name(item).replace(' ', '_')


if __name__ == '__main__':
    unittest.main()
