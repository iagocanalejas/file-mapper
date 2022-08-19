from typing import Optional

from src.core.types import Language
from src.core.types import MediaType
from src.core.types import PathType

media_type: Optional[MediaType] = None
path_type: Optional[PathType] = None
language: Optional[Language] = None

wikipedia_url: Optional[str] = None
mal_url: Optional[str] = None


def __str__():
    return f"""
        media_type: {media_type}
        path_type: {path_type}
        language: {language}
        wikipedia: {wikipedia_url}
        mal: {mal_url}
    """
