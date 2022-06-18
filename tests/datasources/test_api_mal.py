import unittest

import responses

from src.datasources.api import MalAPI
from src.models.metadata import AnimeMetadata
from tests.test import CommonTest


class TestMalAPI(CommonTest):

    def setUp(self) -> None:
        super(TestMalAPI, self).setUp()
        self.responses = responses.RequestsMock()
        self.responses.start()

    def test_find_anime(self):
        anime_id = 37403
        anime_name = 'Ahiru no Sora'
        data = self._load_json('mal_ahiru_no_sora.json')

        self.responses.add(responses.GET, url=f'{MalAPI.BASE_URL}/anime?q={anime_name}', json=data)

        self.assertEqual(MalAPI().find_anime(anime_name), anime_id)

    def test_get_anime_details(self):
        anime_id = 37403
        anime_name = 'Ahiru no Sora'
        data = self._load_json('mal_ahiru_no_sora_details.json')

        self.responses.add(
            responses.GET,
            url=f'{MalAPI.BASE_URL}/anime/{anime_id}?fields=id,title,alternative_titles,media_type',
            json=data
        )

        self.assertEqual(MalAPI().get_anime_details(anime_id), AnimeMetadata(
            mal_id=anime_id,
            title=anime_name,
            media_type=data['media_type'],
            alternative_titles=data['alternative_titles']
        ))


if __name__ == '__main__':
    unittest.main()
