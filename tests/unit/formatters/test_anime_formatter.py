import unittest
from typing import List, Tuple

from src.core.models import Episode, Season
from src.formatter import Formatter
from src.matchers import MediaType
from src.parsers import Parser
from tests.factories import EpisodeFactory, AnimeMetadataFactory, SeasonFactory


# noinspection LongLine
class TestAnimeEpisodeFormatter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)
        cls.formatter = Formatter(media_type=MediaType.ANIME)

    def test_new_name(self):
        pairs: List[Tuple[Episode, str]] = [
            (self.__create_factory('[Judas] Ahiru no Sora - S01E01.mkv', 'Ahiru no Sora', 'Boys Without Talent'), 'Ahiru no Sora - 01 - Boys Without Talent.mkv'),
            (self.__create_factory('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', 'Great Pretender', 'CASE1_2: Los Angeles Connection'), 'Great Pretender - 02 - Case1_2: Los Angeles Connection.mkv'),
            (self.__create_factory('[SubsPlease] Tate no Yuusha no Nariagari S2 - 08 (1080p) [1B2526A8].mkv', 'Tate no Yuusha no Nariagari S2', 'A Parting in the Snow'), 'Tate no Yuusha no Nariagari S2 - 08 - A Parting in the Snow.mkv'),
            (self.__create_factory('[Anipakku] Overlord 01.mkv', 'Overlord', 'A Parting in the Snow'), 'Overlord - 01 - A Parting in the Snow.mkv'),
        ]
        for episode, expected in pairs:
            with self.subTest(name=f'episode:: {episode.item_name}'):
                self.assertEqual(self.formatter.new_name(episode, self.parser), expected)

    @staticmethod
    def __create_factory(item_name: str, title: str, episode_name: str) -> Episode:
        return EpisodeFactory.create(
            item_name=item_name,
            _metadata=AnimeMetadataFactory.create(
                title=title,
                episode_name=episode_name,
            )
        )


# noinspection LongLine
class TestAnimeSeasonFormatter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)
        cls.formatter = Formatter(media_type=MediaType.ANIME)

    def test_season_new_name(self):
        pairs: List[Tuple[Season, str]] = [
            (self.__create_factory('Kobayashi-san Chi no Maid Dragon [v3][1080]', 'Kobayashi-san Chi no Maid Dragon'), 'Kobayashi-san Chi no Maid Dragon'),
            (self.__create_factory('Great Pretender', 'Great Pretender'), 'Great Pretender'),
            (self.__create_factory('Seikon no Qwaser II', 'Seikon no Qwaser II'), 'Seikon no Qwaser II'),
        ]
        for season, expected in pairs:
            with self.subTest(name=f'season:: {season.item_name}'):
                assert isinstance(season, Season)
                self.assertEqual(self.formatter.new_name(season, self.parser), expected)

    @staticmethod
    def __create_factory(item_name: str, title: str) -> Season:
        return SeasonFactory.create(
            item_name=item_name,
            _metadata=AnimeMetadataFactory.create(
                title=title,
            )
        )


if __name__ == '__main__':
    unittest.main()
