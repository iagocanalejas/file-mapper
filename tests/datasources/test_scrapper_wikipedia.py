import re
import unittest

import responses

from src.core import MediaType
from src.datasources.scrapper import WikipediaScrapper
from src.models.metadata import AnimeMetadata
from tests.media.mocks import EpisodeMock
from tests.test import CommonTest


class TestWikipediaScrapper(CommonTest):

    def setUp(self) -> None:
        super(TestWikipediaScrapper, self).setUp()
        self.responses = responses.RequestsMock()
        self.responses.start()

    def test_load_from_episode_page(self):
        data = self._load_page('wikipedia_episode_page_great_pretender.html')
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        file = EpisodeMock(
            _media_type=MediaType.ANIME,
            _metadata=self.__empty_metadata()
        )

        WikipediaScrapper().fill_episode_name(file)
        self.assertEqual(file.episode_name, 'CASE1_1: Los Angeles Connection')

    def test_load_from_main_page(self):
        data = self._load_page('wikipedia_main_page_ahiru_no_sora.html')
        self.responses.add(responses.GET, url=re.compile('.*'), status=404)
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        file = EpisodeMock(
            episode=2,
            _media_type=MediaType.ANIME,
            _metadata=self.__empty_metadata()
        )

        WikipediaScrapper().fill_episode_name(file)
        self.assertEqual(file.episode_name, 'Boys Without Talent')

    def test_load_from_episode_page_2(self):
        data = self._load_page('wikipedia_episode_page_seikon_no_qwaser.html')
        self.responses.add(responses.GET, url=re.compile('.*'), body=data)

        file = EpisodeMock(
            season=2,
            episode=2,
            _media_type=MediaType.ANIME,
            _metadata=self.__empty_metadata()
        )

        WikipediaScrapper().fill_episode_name(file)
        self.assertEqual(file.episode_name, 'The Location of the Magdalene')

    @staticmethod
    def __empty_metadata() -> AnimeMetadata:
        return AnimeMetadata(
            title='',
            mal_id=1,
            media_type='',
            alternative_titles={},
        )


if __name__ == '__main__':
    unittest.main()
