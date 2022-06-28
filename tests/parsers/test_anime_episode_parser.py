import unittest
from typing import List, Tuple, Optional

from src.matchers import MediaType
from src.parsers import Parser
from tests.factories import EpisodeFactory
from tests.test import CommonTest


# noinspection LongLine
class TestAnimeEpisodeParser(CommonTest):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)

    def setUp(self) -> None:
        self.episode = EpisodeFactory()

    def test_episode(self):
        pairs: List[Tuple[str, int]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 1),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 2),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 8),
            ('[Anipakku] Overlord E01.mkv', 1),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'episode:: {name}'):
                self.episode.item_name = name
                self.assertEqual(expected, self.parser.episode(self.episode))

    def test_episode_name_no_metadata(self):
        pairs: List[Tuple[str, int]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 1),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 2),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 8),
            ('[Anipakku] Overlord E01.mkv', 1),
        ]
        # TODO

    def test_season(self):
        pairs: List[Tuple[str, int]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 1),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 1),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 2),
            ('[Anipakku] Overlord E01.mkv', 1),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season:: {name}'):
                self.episode.item_name = name
                self.assertEqual(expected, self.parser.season(self.episode))

    def test_season_name_no_metadata(self):
        pairs: List[Tuple[str, Optional[str]]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', None),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', None),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 'S2'),
            ('[Anipakku] Overlord E01.mkv', None),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season_name:: {name}'):
                self.episode.item_name = name
                self.episode._metadata = None
                self.assertEqual(expected, self.parser.season_name(self.episode))

    def test_media_title_no_metadata(self):
        pairs: List[Tuple[str, str]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 'Ahiru no Sora'),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 'Great Pretender'),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 'Tate no Yuusha no Nariagari'),
            ('[Anipakku] Overlord E01.mkv', 'Overlord'),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'media_title:: {name}'):
                self.episode.item_name = name
                self.episode._metadata = None
                self.assertEqual(expected, self.parser.media_title(self.episode))

    def test_extension(self):
        pairs: List[Tuple[str, str]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 'mkv'),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'extension:: {name}'):
                self.episode.item_name = name
                self.assertEqual(expected, self.parser.extension(self.episode))


if __name__ == '__main__':
    unittest.main()
