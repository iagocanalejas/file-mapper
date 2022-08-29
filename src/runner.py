from typing import Optional

from src.core.types import Language
from src.core.types import MediaType
from src.core.types import PathType
from src.core.types import SubtitleAction

media_type: Optional[MediaType] = None
path_type: Optional[PathType] = None
language: Optional[Language] = None
subs_acton: Optional[SubtitleAction] = None

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
