from dataclasses import dataclass

from src.core import MediaType
from src.models import Episode


@dataclass
class EpisodeMock(Episode):
    base_path: str = ''
    item_name: str = ''
    new_name: str = ''
    season: int = 1
    episode: int = 1
    extension: str = 1
    media_type: MediaType = MediaType.ANIME

    def rename(self):
        pass
