import unittest
from unittest import mock

import responses

from src.core.models import Episode, Season, Show
from src.matchers import MediaType
from src.processors import Processor
from tests.integration.setup import TEST_OBJECTS
from tests.utils import configure_test


class TestAnimeProcessor(unittest.TestCase):
    processor: Processor

    @classmethod
    def setUpClass(cls) -> None:
        cls.processor = Processor(media_type=MediaType.ANIME)

    def setUp(self) -> None:
        self.responses = responses.RequestsMock()
        self.responses.start()

    @mock.patch('os.rename')
    def test_process_episodes(self, mock_rename):
        mock_rename.return_value = None
        for test_object in [t for t in TEST_OBJECTS if t.media_type == MediaType.ANIME and isinstance(t.item, Episode)]:
            configure_test(test_object, self.responses)

            with self.subTest(name=f'testing:: {test_object.item.item_name}'):
                assert isinstance(test_object.item, Episode)
                self.processor.process_episode(test_object.item)

                self.assertEqual(test_object.expected_names[0], test_object.item.item_name)

            self.responses.reset()

    @mock.patch('os.rename')
    def test_process_seasons(self, mock_rename):
        mock_rename.return_value = None
        for test_object in [t for t in TEST_OBJECTS if t.media_type == MediaType.ANIME and isinstance(t.item, Season)]:
            configure_test(test_object, self.responses)

            with self.subTest(name=f'testing:: {test_object.item.item_name}'):
                assert isinstance(test_object.item, Season)
                self.processor.process_season(test_object.item)

                self.assertEqual(test_object.expected_names[0], test_object.item.item_name)
                for index, episode in enumerate(test_object.item.episodes):
                    self.assertEqual(test_object.expected_names[index + 1], episode.item_name)

            self.responses.reset()

    @mock.patch('os.rename')
    def test_process_shows(self, mock_rename):
        mock_rename.return_value = None
        for test_object in [t for t in TEST_OBJECTS if t.media_type == MediaType.ANIME and isinstance(t.item, Show)]:
            configure_test(test_object, self.responses)

            with self.subTest(name=f'testing:: {test_object.item.item_name}'):
                assert isinstance(test_object.item, Show)
                self.processor.process_show(test_object.item)

                self.assertEqual(test_object.expected_names[0], test_object.item.item_name)

                counter = 1
                for season in test_object.item.seasons:
                    self.assertEqual(test_object.expected_names[counter], season.item_name)
                    counter += 1
                    for episode in season.episodes:
                        self.assertEqual(test_object.expected_names[counter], episode.item_name)
                        counter += 1

            self.responses.reset()


if __name__ == '__main__':
    unittest.main()
