import itertools
import os
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from difflib import SequenceMatcher
from typing import Iterable
from typing import List
from typing import Optional

from src import settings
from src.utils.strings import apply_clean
from src.utils.strings import generic_clean
from src.utils.strings import remove_episode
from src.utils.strings import remove_extension
from src.utils.strings import remove_parenthesis
from src.utils.strings import remove_tracker
from src.utils.strings import retrieve_extension


@dataclass
class Item(ABC):
    base_path: str
    name: str

    @property
    def path(self) -> str:
        return os.path.join(self.base_path, self.name)

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        pass


@dataclass
class File(Item):
    __INVALID_EXTENSIONS = ['txt', 'exe']
    parent: Optional['Directory'] = None

    @property
    def is_valid(self) -> bool:
        return (
                self.extension not in self.__INVALID_EXTENSIONS
                and not self.name.startswith('.')  # Dot files
        )

    @property
    def extension(self) -> Optional[str]:
        return retrieve_extension(self.name)


@dataclass
class Directory(Item):
    __SPECIAL_FOLDERS = ['subs', 'extras', 'samples']
    parent: Optional['Directory'] = None
    childs: List[Item] = field(default_factory=list)

    @property
    def depth(self) -> int:
        return 0 if self.parent is None else self.parent.depth + 1

    @property
    def is_valid(self) -> bool:
        return self.name.lower() not in self.__SPECIAL_FOLDERS

    @property
    def can_be_season(self) -> bool:
        return (
                self.has_only_files(ignore_invalid=True)
                and self.__items_can_share_season([i.name for i in self.childs])
        )

    @property
    def can_be_show(self) -> bool:
        """
        :return: Match if all items are files or seasons, and we have at least one directory (season) inside.
        """
        return all(
            isinstance(i, File)  # Files
            or (isinstance(i, Directory) and not i.is_valid)  # Invalid directories
            or (isinstance(i, Directory) and i.is_valid and i.can_be_season)  # Season directories

            for i in self.childs
        ) and not self.has_only_files(ignore_invalid=True)

    def has_only_files(self, ignore_invalid=False) -> bool:
        if ignore_invalid:
            return all(isinstance(i, File) or (isinstance(i, Directory) and not i.is_valid) for i in self.childs)
        return all(isinstance(i, File) for i in self.childs)

    @staticmethod
    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_parenthesis, remove_episode, remove_extension])
    def __items_can_share_season(items: Iterable[str]) -> bool:
        """
        Check if all files share enough similarity to be considered of the same season or all strings match 'S1E01'
        :param items: list of files to check
        :return: bool expressing if the list can be considered a season
        """
        ratios = [SequenceMatcher(None, i[0], i[1]).ratio() for i in itertools.permutations(items, 2)]
        se = re.compile(r'^(S\d+E\d+|E\d+).*')  # probably a limit case
        return all(r >= settings.SIMILARITY_THRESHOLD for r in ratios) or all(se.match(s) for s in items)
