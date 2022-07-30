from dataclasses import dataclass
from typing import Optional

from src.core.types import Language
from src.matchers import MediaType


@dataclass
class GlobalConfig:
    media_type: Optional[MediaType] = None
    language: Optional[Language] = None

    # Ensure only one GlobalConfig exists
    __instance: Optional['GlobalConfig'] = None

    def __new__(cls, *args, **kwargs) -> 'GlobalConfig':  # pragma: no cover
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
