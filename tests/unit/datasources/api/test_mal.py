import os.path
import unittest
from unittest import mock

import responses

from src.core.models.metadata import AnimeMetadata
from src.datasources.api import MalAPI
from tests import settings
from tests.utils import load_json


class TestMalAPI(unittest.TestCase):

    def setUp(self) -> None:
        super(TestMalAPI, self).setUp()
        self.responses = responses.RequestsMock()
        self.responses.start()

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_find_anime(self, mock_parser):
        anime_name = 'Ahiru no Sora'
        data = load_json(os.path.join(settings.MAL_FIXTURES_DIR, 'ahiru_no_sora.json'))

        self.responses.add(responses.GET, url=f'{MalAPI.BASE_URL}/anime?q={anime_name}', json=data)

        self.assertEqual(MalAPI(mock_parser).search_anime(anime_name), [('Ahiru no Sora', 37403),
                                                                        ('Chiruran: Nibun no Ichi', 34088),
                                                                        ('Kami nomi zo Shiru Sekai II', 10080),
                                                                        ('Sora no Aosa wo Shiru Hito yo', 39569),
                                                                        ('Ahiru no Ko', 35410),
                                                                        ('Kami nomi zo Shiru Sekai: Megami-hen', 16706),
                                                                        ('Ahiru no Otegara', 6852),
                                                                        ('Sora no Method', 23209)])

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_get_anime_details(self, mock_parser):
        anime_id = 37403
        anime_name = 'Ahiru no Sora'
        data = load_json(os.path.join(settings.MAL_FIXTURES_DIR, 'ahiru_no_sora_details.json'))

        self.responses.add(
            responses.GET,
            url=f'{MalAPI.BASE_URL}/anime/{anime_id}?fields=id,title,alternative_titles,media_type',
            json=data
        )

        self.assertEqual(MalAPI(mock_parser).get_anime_details(anime_id), AnimeMetadata(
            datasource_id=anime_id,
            datasource=MalAPI.DATASOURCE,
            title=anime_name,
            alternative_titles=data['alternative_titles']
        ))


if __name__ == '__main__':
    unittest.main()
