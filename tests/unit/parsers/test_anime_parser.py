import unittest
from typing import List
from typing import Optional
from typing import Tuple

from src.filemapper.matchers import MediaType
from src.filemapper.parsers import Parser
from tests.factories import EpisodeFactory
from tests.factories import SeasonFactory


# noinspection LongLine
class TestAnimeEpisodeParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)

    def test_episode(self):
        pairs: List[Tuple[str, int]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 1),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 2),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 8),
            ('[Anipakku] Overlord E01.mkv', 1),
            ('The Case Study of Vanitas S01E12.5-Recap [E94DA148].mkv', 12)
        ]
        for name, expected in pairs:
            with self.subTest(name=f'episode:: {name}'):
                episode = EpisodeFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.episode(episode))

    def test_episode_part(self):
        pairs: List[Tuple[str, int]] = [
            ('[Anipakku] Overlord E01.mkv', None),
            ('The Case Study of Vanitas S01E12.5-Recap [E94DA148].mkv', 5)
        ]
        for name, expected in pairs:
            with self.subTest(name=f'episode:: {name}'):
                episode = EpisodeFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.episode_part(episode))

    def test_season(self):
        pairs: List[Tuple[str, int]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 1),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 1),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 2),
            ('[Anipakku] Overlord E01.mkv', 1),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season:: {name}'):
                episode = EpisodeFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.season(episode))

    def test_season_name_no_metadata(self):
        pairs: List[Tuple[str, Optional[str]]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', None),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', None),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 'S2'),
            ('[Anipakku] Overlord E01.mkv', None),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season_name:: {name}'):
                episode = EpisodeFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.season_name(episode))

    def test_media_title_no_metadata(self):
        pairs: List[Tuple[str, str]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 'Ahiru no Sora'),
            ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 'Great Pretender'),
            ('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 'Tate no Yuusha no Nariagari'),
            ('[Anipakku] Overlord E01.mkv', 'Overlord'),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'media_title:: {name}'):
                episode = EpisodeFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.media_title(episode))

    def test_extension(self):
        pairs: List[Tuple[str, str]] = [
            ('[Judas] Ahiru no Sora - S01E01.mkv', 'mkv'),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'extension:: {name}'):
                episode = EpisodeFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.extension(episode))


# noinspection LongLine
class TestAnimeSeasonParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)

    def test_season(self):
        pairs: List[Tuple[str, int]] = [
            ('Kobayashi-san Chi no Maid Dragon [v3][1080]', 1),
            ('Great Pretender', 1),
            ('Seikon no Qwaser II', 2),
            ('[Judas] Tate no Yuusha no Noriagari (The Rising of the Shield Hero) (Season 2) [1080p][HEVC x265 10bit][Multi-Subs]', 2)
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season:: {name}'):
                season = SeasonFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.season(season))

    def test_season_name_no_metadata(self):
        pairs: List[Tuple[str, Optional[str]]] = [
            ('Kobayashi-san Chi no Maid Dragon [v3][1080]', None),
            ('Great Pretender', None),
            ('Seikon no Qwaser II', 'II'),
            ('[Judas] Tate no Yuusha no Noriagari (The Rising of the Shield Hero) (Season 2) [1080p][HEVC x265 10bit][Multi-Subs]', 'S2')
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season_name:: {name}'):
                season = SeasonFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.season_name(season))

    def test_media_title_no_metadata(self):
        pairs: List[Tuple[str, str]] = [
            ('Kobayashi-san Chi no Maid Dragon [v3][1080]', 'Kobayashi-san Chi no Maid Dragon'),
            ('Great Pretender', 'Great Pretender'),
            ('Seikon no Qwaser II', 'Seikon no Qwaser'),
            ('[Judas] Tate no Yuusha no Noriagari (The Rising of the Shield Hero) (Season 2) [1080p][HEVC x265 10bit][Multi-Subs]', 'Tate no Yuusha no Noriagari')
        ]
        for name, expected in pairs:
            with self.subTest(name=f'media_title:: {name}'):
                season = SeasonFactory.create(item_name=name)
                self.assertEqual(expected, self.parser.media_title(season))


if __name__ == '__main__':
    unittest.main()
