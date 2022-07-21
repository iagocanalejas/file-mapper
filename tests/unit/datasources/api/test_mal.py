import os.path
import unittest
from unittest import mock

import responses

from src.core.models.metadata import AnimeMetadata
from src.core.types import DatasourceName
from src.core.types import Language
from src.datasources.api import MalAPI
from tests import settings
from tests.utils import load_json


class TestMalAPI(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.responses = responses.RequestsMock()
        self.responses.start()

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_find_anime(self, mock_parser):
        anime_name = 'Ahiru no Sora'

        url = MalAPI.BASE_URL.format(anime=anime_name)
        data = load_json(os.path.join(settings.MAL_FIXTURES_DIR, 'ahiru_no_sora.json'))
        self.responses.add(responses.GET, url=url, json=data)

        self.assertEqual(AnimeMetadata(title='Ahiru no Sora',
                                       title_lang=Language.JA,
                                       datasource_data={DatasourceName.MAL: '37403'},
                                       alternative_titles={'en': '', 'ja': 'あひるの空', 'synonyms': []},
                                       season_name=None,
                                       episode_name=None),
                         MalAPI(mock_parser).search_anime(anime_name, Language.JA, 1, ''))


if __name__ == '__main__':
    unittest.main()
