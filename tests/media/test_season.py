import unittest
from typing import List
from unittest import mock

from src.core import MediaType
from src.models import Season
from src.models.metadata import AnimeMetadata
from tests.media.mocks import SeasonContainer, ExpectedSeason, mock_anime_file
from tests.test import CommonTest


class TestSeason(CommonTest):
    seasons: List[SeasonContainer] = [
        SeasonContainer(
            item_name='Kobayashi-san Chi no Maid Dragon [v3][1080]',
            title='Kobayashi-san Chi no Maid Dragon',
            episodes=[],
            expected=ExpectedSeason(
                media_name='Kobayashi-san Chi no Maid Dragon',
                new_name='Kobayashi-san Chi no Maid Dragon',
                season=1,
            )
        ),
        SeasonContainer(
            item_name='Great Pretender',
            title='Great Pretender',
            episodes=[
                mock_anime_file(name='[Cleo]Great_Pretender_-_01_(Dual Audio_10bit_1080p_x265).mkv'),
                mock_anime_file(name='[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv')
            ],
            expected=ExpectedSeason(
                media_name='Great Pretender',
                new_name='Great Pretender',
                season=1,
            )
        ),
        SeasonContainer(
            item_name='Seikon no Qwaser II',
            title='Seikon no Qwaser II',
            episodes=[],
            expected=ExpectedSeason(
                media_name='Seikon no Qwaser II',
                new_name='Seikon no Qwaser II',
                season=2,
            )
        ),
    ]

    def test_anime_season(self):
        for item in self.seasons:
            item.season.media_type = MediaType.ANIME
            with self.subTest(name=f'season :: {item.season.item_name}'):
                self.assertEqual(item.season.new_name, item.expected.new_name)
                self.assertEqual(item.season.media_name, item.expected.media_name)
                self.assertEqual(item.season.season, item.expected.season)

    def test_metadata_consistency(self):
        metadata = AnimeMetadata(mal_id=1, title='', media_type='', alternative_titles={})
        season = Season(base_path='', item_name='', episodes=[mock_anime_file(), mock_anime_file()])

        season.metadata = metadata

        self.assertEqual(season.episodes[0].metadata, metadata)
        self.assertEqual(season.episodes[1].metadata, metadata)

    @mock.patch('os.rename')
    def test_rename(self, mock_rename):
        for item in self.seasons:
            item.season.media_type = MediaType.ANIME
            # required to set the metadata for the files
            item.season.metadata = item.season.metadata
            [setattr(f.metadata, 'episode_name', 'test_name') for f in item.season.episodes]

            with self.subTest(name=f'rename :: {item.season.item_name}'):
                item.season.rename()

                mock_rename.assert_called()
                self.assertEqual(item.season.item_name, item.expected.new_name)
                self.assertTrue(all([f.item_name == f.new_name for f in item.season.episodes]))


if __name__ == '__main__':
    unittest.main()
