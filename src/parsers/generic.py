from src.core import MediaType
from src.core.exceptions import UnsupportedMediaType
from src.parsers._parser import Parser


class GenericParser(Parser, media_type=MediaType.UNKNOWN):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.UNKNOWN, **kwargs)
        return cls._instance

    def matches(self, name: str, **kwargs) -> bool:
        raise UnsupportedMediaType()

    @staticmethod
    def season(word: str) -> int:
        raise UnsupportedMediaType()

    @staticmethod
    def episode(word: str) -> int:
        raise UnsupportedMediaType()

    @staticmethod
    def media_name(word: str) -> str:
        raise UnsupportedMediaType()
