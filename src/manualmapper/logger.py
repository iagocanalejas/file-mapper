import csv
import os
from dataclasses import dataclass
from typing import Dict
from typing import Optional


@dataclass
class _NamingMap:
    original: str
    new_name: Optional[str] = None


class OutputLog:
    _instance = None
    _lmap: Dict[int, _NamingMap] = {}

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def insert(self, key: int, value: str):
        self._lmap[key] = _NamingMap(original=value)

    def update(self, key: int, value: str):
        self._lmap[key].new_name = value

    def log(self, item, to: str):
        file_path = os.path.join(item.base_path, to)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['original_name', 'new_name'])
            [writer.writerow([row.original, row.new_name]) for row in self._lmap.values() if row.new_name]
