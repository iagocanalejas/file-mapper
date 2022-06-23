import json
import os
import unittest


class CommonTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    @staticmethod
    def _load_page(path: str):
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_fixtures', 'pages', path)
        with open(full_path, 'r') as f:
            data = f.read()
            f.close()
        return data

    @staticmethod
    def _load_json(path: str):
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_fixtures', 'json', path)
        with open(full_path, 'r') as f:
            data = json.load(f)
            f.close()
        return data
