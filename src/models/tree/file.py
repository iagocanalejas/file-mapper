from dataclasses import dataclass

from src.models.item import Item
from src.models.media.episode import Episode


@dataclass
class File(Item):
    @staticmethod
    def is_valid_file(name: str) -> bool:
        extension = name.split('.')[-1]
        return extension != 'txt' and extension != 'exe'

    def to_episode(self) -> Episode:
        return Episode(
            base_path=self.base_path,
            item_name=self.item_name
        )

    def rename(self):
        raise NotImplementedError
