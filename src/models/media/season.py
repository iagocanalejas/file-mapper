import os
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

import settings
from src.core import MediaType
from src.core.exceptions import UnsupportedMediaType
from src.models.item import MediaItem
from src.models.media.episode import Episode
from src.models.metadata import Metadata, AnimeMetadata


@dataclass
class Season(MediaItem):
    episodes: List[Episode] = field(default_factory=list)

    @MediaItem.media_type.setter
    def media_type(self, value: MediaType):
        MediaItem.media_type.fset(self, value)  # Call to the super method
        for file in self.episodes:
            file.media_type = value

    @MediaItem.metadata.setter
    def metadata(self, value: Metadata):
        MediaItem.metadata.fset(self, value)  # Call to the super method
        for file in self.episodes:
            file.metadata = deepcopy(value)

    @property
    def season(self) -> int:
        return self._parser.season(self.item_name)

    @property
    def new_name(self) -> str:
        if self.media_type == MediaType.ANIME:
            assert isinstance(self._metadata, AnimeMetadata)
            return f'{self._metadata.title}'

        raise UnsupportedMediaType(f'{self}')

    def rename(self):
        for f in self.episodes:
            f.rename()

        if not settings.MOCK_RENAME:
            os.rename(self.full_path, os.path.join(self.base_path, self.new_name))
        super(Season, self).rename()
