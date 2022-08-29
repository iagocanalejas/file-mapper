from src.core.formatter._formatter import Formatter
from src.core.models import MediaItem
from src.core.models import SubsFile
from src.core.types import Language
from src.core.types import MediaType
from src.core.utils.strings import remove_extension


class SubsFormatter(Formatter, media_type=MediaType.SUBS):
    _instance = None

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, media_type=MediaType.SUBS, **kwargs)
        return cls._instance

    def new_name(self, item: SubsFile) -> str:
        assert item.parent is not None
        return self.format(item, pattern='{parent}_{language}.{extension}')

    def format(self, item: SubsFile, pattern: str, **kwargs) -> str:
        assert item.parent is not None

        return pattern.format(
            parent=remove_extension(item.parent.item_name),
            language=item.language,
            extension=item.parsed.extension,
        )
