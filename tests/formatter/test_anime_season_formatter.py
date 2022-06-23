import unittest
from typing import List, Tuple

from src.core.models import Season
from src.formatter import Formatter
from src.matchers import MediaType
from src.parsers import Parser
from tests.factories import AnimeMetadataFactory, SeasonFactory
from tests.test import CommonTest


# noinspection LongLine
class TestAnimeSeasonFormatter(CommonTest):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)
        cls.formatter = Formatter(media_type=MediaType.ANIME)

    def test_season_new_name(self):
        pairs: List[Tuple[SeasonFactory, str]] = [
            (self.__create_factory('Kobayashi-san Chi no Maid Dragon [v3][1080]', 'Kobayashi-san Chi no Maid Dragon'), 'Kobayashi-san Chi no Maid Dragon'),
            (self.__create_factory('Great Pretender', 'Great Pretender'), 'Great Pretender'),
            (self.__create_factory('Seikon no Qwaser II', 'Seikon no Qwaser II', True), 'Seikon no Qwaser II'),
        ]
        for season, expected in pairs:
            with self.subTest(name=f'season:: {season.item_name}'):
                assert isinstance(season, Season)
                self.assertEqual(self.formatter.new_name(self.parser, season), expected)

    @staticmethod
    def __create_factory(item_name: str, title: str, seasoned: bool = False) -> SeasonFactory:
        return SeasonFactory.create(
            item_name=item_name,
            _metadata=AnimeMetadataFactory.create(
                title=title,
                seasoned=seasoned,
            )
        )


if __name__ == '__main__':
    unittest.main()
