import unittest
from unittest import mock

import responses

from src.core.models.metadata import AnimeMetadata
from src.datasources.api import MalAPI
from tests.test import CommonTest


class TestMalAPI(CommonTest):

    def setUp(self) -> None:
        super(TestMalAPI, self).setUp()
        self.responses = responses.RequestsMock()
        self.responses.start()

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_find_anime(self, mock_parser):
        anime_id = 37403
        anime_name = 'Ahiru no Sora'
        data = self._load_json('mal_ahiru_no_sora.json')

        self.responses.add(responses.GET, url=f'{MalAPI.BASE_URL}/anime?q={anime_name}', json=data)

        self.assertEqual(MalAPI(mock_parser).find_anime(anime_name), anime_id)

    @mock.patch('src.parsers.anime.AnimeParser')
    def test_get_anime_details(self, mock_parser):
        anime_id = 37403
        anime_name = 'Ahiru no Sora'
        data = self._load_json('mal_ahiru_no_sora_details.json')

        self.responses.add(
            responses.GET,
            url=f'{MalAPI.BASE_URL}/anime/{anime_id}?fields=id,title,alternative_titles,media_type',
            json=data
        )

        self.assertEqual(MalAPI(mock_parser).get_anime_details(anime_id), AnimeMetadata(
            datasource_id=anime_id,
            title=anime_name,
            media_type=data['media_type'],
            alternative_titles=data['alternative_titles']
        ))


if __name__ == '__main__':
    unittest.main()
