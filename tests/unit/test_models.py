import unittest
from typing import List

from tests.factories import DirectoryFactory
from tests.factories import FileFactory


class TestModels(unittest.TestCase):
    seasons: List[List[str]] = [
        [
            'Great Pretender',
            '[Cleo]Great_Pretender_-_01_(Dual Audio_10bit_1080p_x265).mkv',
            '[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv',
            '[Cleo]Great_Pretender_-_03_(Dual Audio_10bit_1080p_x265).mkv',
        ],
        [
            'Kaguya-sama wa Kokurasetai Tensai-tachi no Renai Zunousen BD',
            '[DB]Kaguya-sama wa Kokurasetai Tensai-tachi no Renai Zunousen_-_01_(10bit_BD1080p_x265).mkv',
            '[DB]Kaguya-sama wa Kokurasetai Tensai-tachi no Renai Zunousen_-_02_(10bit_BD1080p_x265).mkv',
            '[DB]Kaguya-sama wa Kokurasetai Tensai-tachi no Renai Zunousen_-_03_(10bit_BD1080p_x265).mkv',
        ]
    ]

    def test_can_be_season(self):
        for season in self.seasons:
            directory = DirectoryFactory.create(name=season[0], childs=[FileFactory.create(name=n) for n in season[1:]])
            with self.subTest(name=f'matches:: {directory}'):
                self.assertTrue(directory.can_be_season)


if __name__ == '__main__':
    unittest.main()
