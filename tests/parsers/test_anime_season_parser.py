import unittest
from typing import List, Tuple, Optional

from src.matchers import MediaType
from src.parsers import Parser
from tests.factories import SeasonFactory
from tests.test import CommonTest


# noinspection LongLine
class TestAnimeSeasonParser(CommonTest):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = Parser(media_type=MediaType.ANIME)

    def setUp(self) -> None:
        self.season = SeasonFactory()

    def test_season(self):
        pairs: List[Tuple[str, int]] = [
            ('Kobayashi-san Chi no Maid Dragon [v3][1080]', 1),
            ('Great Pretender', 1),
            ('Seikon no Qwaser II', 2),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season:: {name}'):
                season = SeasonFactory(item_name=name)
                self.assertEqual(self.parser.season(season), expected)

    def test_season_name_no_metadata(self):
        pairs: List[Tuple[str, Optional[str]]] = [
            ('Kobayashi-san Chi no Maid Dragon [v3][1080]', None),
            ('Great Pretender', None),
            ('Seikon no Qwaser II', 'II'),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season_name:: {name}'):
                self.season.item_name = name
                self.season._metadata = None
                self.assertEqual(self.parser.season_name(self.season), expected)

    def test_media_name_no_metadata(self):
        pairs: List[Tuple[str, str]] = [
            ('Kobayashi-san Chi no Maid Dragon [v3][1080]', 'Kobayashi-san Chi no Maid Dragon'),
            ('Great Pretender', 'Great Pretender'),
            ('Seikon no Qwaser II', 'Seikon no Qwaser II'),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'media_name:: {name}'):
                self.season.item_name = name
                self.season._metadata = None
                self.assertEqual(self.parser.media_name(self.season), expected)

    def test_is_seasoned(self):
        pairs: List[Tuple[str, bool]] = [
            ('Kobayashi-san Chi no Maid Dragon', False),
            ('Great Pretender', False),
            ('Seikon no Qwaser II', True),
        ]
        for name, expected in pairs:
            with self.subTest(name=f'season:: {name}'):
                self.season.metadata.title = name
                self.assertEqual(self.parser.is_seasoned_media_name(self.season), expected)


if __name__ == '__main__':
    unittest.main()
