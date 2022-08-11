from src.core.exceptions import UnsupportedMediaType
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.types import MediaType
from src.filemapper.processors import Processor


class UnknownProcessor(Processor, media_type=MediaType.UNKNOWN):
    _instance = None

    def __new__(cls, *args, **kwargs):  # pragma: no cover
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
