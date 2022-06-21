import unittest
from typing import List
from unittest import mock

from src.core import MediaType
from src.models import Episode
from tests.media.mocks import EpisodeContainer, ExpectedEpisode
from tests.test import CommonTest


class TestEpisode(CommonTest):
    files: List[EpisodeContainer] = [
        EpisodeContainer(
            item_name='[Judas] Ahiru no Sora - S01E01.mkv',
            title='Ahiru no Sora',
            episode_name='Boys Without Talent',
            expected=ExpectedEpisode(
                media_name='Ahiru no Sora',
                new_name='Ahiru no Sora - 01 - Boys Without Talent.mkv',
                season=1,
                episode=1,
                extension='mkv',
            )
        ),
        EpisodeContainer(
            item_name='[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv',
            title='Great Pretender',
            episode_name='CASE1_2: Los Angeles Connection',
            expected=ExpectedEpisode(
                media_name='Great Pretender',
                new_name='Great Pretender - 02 - Case1_2: Los Angeles Connection.mkv',
                season=1,
                episode=2,
                extension='mkv',
            )
        ),
        EpisodeContainer(
            item_name='[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv',
            title='Tate no Yuusha no Nariagari Season 2',
            episode_name='A Parting in the Snow',
            expected=ExpectedEpisode(
                media_name='Tate no Yuusha no Nariagari Season 2',
                new_name='Tate no Yuusha no Nariagari S2 - 08 - A Parting In The Snow.mkv',
                season=2,
                episode=8,
                extension='mkv',
            )
        ),
        EpisodeContainer(
            item_name='[Anipakku] Overlord E01.mkv',
            title='Overlord',
            episode_name='A Parting in the Snow',
            expected=ExpectedEpisode(
                media_name='Overlord',
                new_name='Overlord - 01 - A Parting In The Snow.mkv',
                season=1,
                episode=1,
                extension='mkv',
            )
        ),
    ]

    def test_is_valid(self):
        self.assertFalse(Episode.is_valid_file('[Anipakku] Overlord 01.exe'))
        self.assertFalse(Episode.is_valid_file('[Anipakku] Overlord 01.txt'))

        self.assertTrue(Episode.is_valid_file('[Anipakku] Overlord 01.mkv'))

    def test_anime_file(self):
        for item in self.files:
            item.episode.media_type = MediaType.ANIME
            with self.subTest(name=f'file :: {item.episode.item_name}'):
                self.assertEqual(item.episode.media_name, item.expected.media_name)
                self.assertEqual(item.episode.new_name, item.expected.new_name)
                self.assertEqual(item.episode.episode, item.expected.episode)
                self.assertEqual(item.episode.season, item.expected.season)
                self.assertEqual(item.episode.extension, item.expected.extension)

    @mock.patch('os.rename')
    def test_rename(self, mock_rename):
        for item in self.files:
            item.episode.media_type = MediaType.ANIME
            with self.subTest(name=f'rename :: {item.episode.item_name}'):
                item.episode.rename()

                mock_rename.assert_called()
                self.assertEqual(item.episode.item_name, item.expected.new_name)


if __name__ == '__main__':
    unittest.main()
