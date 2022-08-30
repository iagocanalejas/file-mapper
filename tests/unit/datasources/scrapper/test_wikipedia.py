import os
import re
import unittest

from aioresponses import aioresponses

from src.core.datasources.scrapper import WikipediaScrapper
from src.core.models import ParsedInfo
from src.core.models.metadata import AnimeMetadata
from src.core.parsers import Parser
from src.core.types import MediaType
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
    def test_load_from_episode_page(self, mocked_response):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_great_pretender.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        self.episode.parsed = ParsedInfo(
            episode=1,
            season=1,
            episode_part=None,
            season_name=None,
            media_title='',
            extension=None
        )

        WikipediaScrapper().fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'CASE1_1: Los Angeles Connection')

    @aioresponses()
    def test_load_from_main_page(self, mocked_response):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'main_page_ahiru_no_sora.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        self.episode.parsed = ParsedInfo(
            episode=2,
            season=1,
            episode_part=None,
            season_name=None,
            media_title='',
            extension=None
        )

        WikipediaScrapper().fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'Boys Without Talent')

    @aioresponses()
    def test_load_from_episode_page_2(self, mocked_response):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_seikon_no_qwaser.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        self.episode.parsed = ParsedInfo(
            episode=2,
            season=2,
            episode_part=None,
            season_name=None,
            media_title='',
            extension=None
        )

        WikipediaScrapper().fill_episode_name(self.episode)

        metadata = self.episode.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.episode_name, 'The Location of the Magdalene')

    @aioresponses()
    def test_load_season_from_episode_page_as_season_x(self, mocked_response):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_hajime_no_ippo.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        self.season.parsed = ParsedInfo(
            episode=1,
            season=1,
            episode_part=None,
            season_name=None,
            media_title='',
            extension=None
        )

        WikipediaScrapper().fill_season_names(self.season)

        metadata = self.season.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.season_name, 'S1: The Fighting!')

    @aioresponses()
    def test_load_season_from_episode_page_as_name(self, mocked_response):
        data = load_page(os.path.join(settings.WIKIPEDIA_FIXTURES_DIR, 'episode_page_seikon_no_qwaser.html'))
        mocked_response.get(re.compile('.*'), status=200, body=data)

        self.season.parsed = ParsedInfo(
            episode=1,
            season=2,
            episode_part=None,
            season_name=None,
            media_title='',
            extension=None
        )

        WikipediaScrapper().fill_season_names(self.season)

        metadata = self.season.metadata
        assert isinstance(metadata, AnimeMetadata)
        self.assertEqual(metadata.season_name, 'II')


if __name__ == '__main__':
    unittest.main()
