from src.core.exceptions import UnsupportedMediaType
from src.core.models import Episode, Season, Show, MediaItem
from src.processors import Processor
from src.matchers import MediaType


class UnknownProcessor(Processor, media_type=MediaType.UNKNOWN):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def process_episode(self, episode: Episode):
        raise UnsupportedMediaType()

    def process_season(self, season: Season):
        raise UnsupportedMediaType()

    def process_show(self, show: Show):
        raise UnsupportedMediaType()

    def rename(self, item: MediaItem):
        raise UnsupportedMediaType()

    @classmethod
    def matches(cls, name: str, **kwargs) -> bool:
        return False
