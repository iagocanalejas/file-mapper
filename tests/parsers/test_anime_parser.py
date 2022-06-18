import unittest
from typing import List, Tuple

from src.parsers import AnimeParser
from tests.test import CommonTest


class TestAnimeParser(CommonTest):
    files: List[Tuple[str, bool]] = [
        ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', True),
        ('[Judas] Ahiru no Sora - S01E02.mkv', True),
        ('Nobody.2021.2160p.BluRay.x265.10bit.SDR.DTS-HD.MA.TrueHD.7.1.Atmos-SWTYBLZ.mkv', False),
    ]

    def test_match(self):
        for file_name, should_pass in self.files:
            with self.subTest(name=file_name):
                self.assertEqual(AnimeParser().matches(file_name), should_pass)


if __name__ == '__main__':
    unittest.main()
