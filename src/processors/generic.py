from src.core import MediaType
from src.core.exceptions import UnsupportedMediaType
from src.models import Episode, Season, Show
from src.processors import Processor


class GenericProcessor(Processor, media_type=MediaType.UNKNOWN):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.UNKNOWN, **kwargs)
        return cls._instance

    def process_episode(self, episode: Episode):
        raise UnsupportedMediaType()

    def process_season(self, season: Season):
        raise UnsupportedMediaType()

    def process_show(self, show: Show):
        raise UnsupportedMediaType()
