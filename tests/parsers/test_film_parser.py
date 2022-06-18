import unittest
from typing import List, Tuple

from src.parsers.film import FilmParser
from tests.test import CommonTest


class TestFilmParser(CommonTest):
    files: List[Tuple[str, bool]] = [
        ('Nobody.2021.2160p.BluRay.x265.10bit.SDR.DTS-HD.MA.TrueHD.7.1.Atmos-SWTYBLZ.mkv', True),
        ('[Cleo]Great_Pretender_-_02_(Dual Audio_10bit_1080p_x265).mkv', False),
    ]

    def test_match(self):
        for file_name, should_pass in self.files:
            with self.subTest(name=file_name):
                self.assertEqual(FilmParser().matches(file_name), should_pass)


if __name__ == '__main__':
    unittest.main()
