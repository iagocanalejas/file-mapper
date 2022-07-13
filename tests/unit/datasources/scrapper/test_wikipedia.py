import os
import re
import unittest
from unittest import mock

from aioresponses import aioresponses

from src.core.models.metadata import AnimeMetadata
from src.datasources.scrapper import WikipediaScrapper
from src.matchers import MediaType
from src.parsers import Parser
from tests import settings
from tests.factories import AnimeMetadataFactory
from tests.factories import EpisodeFactory
from tests.factories import SeasonFactory
from tests.utils import load_page


class TestWikipediaScrapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)

    def setUp(self) -> None:
        super().setUp()

        self.episode = EpisodeFactory.create(item_name='', _metadata=AnimeMetadataFactory())
        self.season = SeasonFactory.create(item_name='', episodes=[], _metadata=AnimeMetadataFactory())

    @aioresponses()
    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_episode_page(self, mocked_response, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_great_pretender.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        mock_parser = self.__setup_mock_parser_defaults(mock_parser)
        mock_parser.episode.return_value = 1
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser).fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'CASE1_1: Los Angeles Connection')

    @aioresponses()
    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_main_page(self, mocked_response, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'main_page_ahiru_no_sora.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        mock_parser = self.__setup_mock_parser_defaults(mock_parser)
        mock_parser.episode.return_value = 2
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser).fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'Boys Without Talent')

    @aioresponses()
    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_from_episode_page_2(self, mocked_response, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_seikon_no_qwaser.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        mock_parser = self.__setup_mock_parser_defaults(mock_parser)
        mock_parser.episode.return_value = 2
        mock_parser.season.return_value = 2

        WikipediaScrapper(mock_parser).fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'The Location of the Magdalene')

    @aioresponses()
    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_season_from_episode_page_as_season_x(self, mocked_response, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_hajime_no_ippo.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        mock_parser = self.__setup_mock_parser_defaults(mock_parser)
        mock_parser.episode.return_value = 1
        mock_parser.season.return_value = 1

        WikipediaScrapper(mock_parser).fill_season_names(self.season)

        metadata = self.season.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.season_name, 'Season 1: The Fighting!')

    @aioresponses()
    @mock.patch('src.parsers.anime.AnimeParser')
    def test_load_season_from_episode_page_as_name(self, mocked_response, mock_parser):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_seikon_no_qwaser.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        mock_parser = self.__setup_mock_parser_defaults(mock_parser)
        mock_parser.episode.return_value = 1
        mock_parser.season.return_value = 2

        WikipediaScrapper(mock_parser).fill_season_names(self.season)

        metadata = self.season.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.season_name, 'II')

    @staticmethod
    def __setup_mock_parser_defaults(parser):
        parser.episode.return_value = 1
        parser.episode_part.return_value = None
        parser.episode_name.return_value = ''
        parser.season.return_value = 1
        parser.season_name.return_value = ''
        parser.media_name.return_value = ''
        parser.media_title.return_value = ''
        parser.extension.return_value = ''

        return parser


if __name__ == '__main__':
    unittest.main()
