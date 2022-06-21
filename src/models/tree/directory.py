import itertools
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import List

import settings
from src.models.item import Item
from src.models.media.season import Season
from src.models.media.show import Show
from src.models.tree.file import File
from src.parsers import Parser
from src.utils.strings import apply_clean, generic_clean, remove_tracker, remove_parenthesis, remove_extension


@dataclass
class Directory(Item):
    items: List[Item] = field(default_factory=list)
    depth: int = 0

    def __str__(self):  # pragma: no cover
        tab = '   '
        st = f"{tab * (self.depth - 1)}{super().__str__()}\n" if self.depth > 0 else f""
        for i in self.items:
            st += f"{tab * self.depth}{i}\n"
        return st

    @property
    def is_valid_folder(self) -> bool:
        return not ('subs' in self.item_name.lower()
                    or 'extras' in self.item_name.lower()
                    or 'sample' in self.item_name.lower())

    @property
    def is_season_folder(self) -> bool:
        return (self.has_only_files(ignore_invalid=True)
                and self.__items_can_share_season([i.item_name for i in self.items]))

    @property
    def is_show_folder(self) -> bool:
        """
        :return: Match if all items are files or seasons, and we have at least one directory (season) inside.
        """
        return all(isinstance(i, File)  # Files
                   or (isinstance(i, Directory) and not i.is_valid_folder)  # Invalid directories
                   or (isinstance(i, Directory) and i.is_valid_folder and i.is_season_folder)  # Season directories
                   for i in self.items) and not self.has_only_files(ignore_invalid=True)

    def has_only_files(self, ignore_invalid=False) -> bool:
        if ignore_invalid:
            return all(isinstance(i, File) or (isinstance(i, Directory) and not i.is_valid_folder) for i in self.items)
        return all(isinstance(i, File) for i in self.items)

    def to_season(self) -> Season:
        return Season(
            base_path=self.base_path,
            item_name=self.item_name,
            episodes=[i.to_episode() for i in self.items if isinstance(i, File)]  # We can only have Files
        )

    def to_show(self) -> Show:
        show = Show(
            base_path=self.base_path,
            item_name=self.item_name,
            files=[i.to_episode() for i in self.items if isinstance(i, File)],
        )

        for subdirectory in [i for i in self.items if isinstance(i, Directory) and i.is_valid_folder]:
            if not subdirectory.has_only_files():
                raise ValueError(f'{self}')
            show.seasons.append(subdirectory.to_season())

        return show

    @staticmethod
    @apply_clean(clean_functions=[generic_clean, remove_tracker, remove_parenthesis, remove_extension])
    def __items_can_share_season(items: List[str]) -> bool:
        """
        Check if all files share enough similarity to be considered of the same season
        :param items: list of files to check
        :return: bool expressing if the list can be considered a season
        """

        seasons = [Parser.season(i) for i in items]
        if not all(s == seasons[0] for s in seasons):
            # We should have matching seasons
            return False

        ratios = [SequenceMatcher(None, i[0], i[1]).ratio() for i in itertools.permutations(items, 2)]
        return all(r > settings.SIMILARITY_THRESHOLD for r in ratios)

    def rename(self):
        raise NotImplementedError
