import os
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

import settings
from src.core import MediaType
from src.models.item import MediaItem
from src.models.media.episode import Episode
from src.models.media.season import Season
from src.models.metadata import Metadata


@dataclass
class Show(MediaItem):
    seasons: List[Season] = field(default_factory=list)
    files: List[Episode] = field(default_factory=list)

    @MediaItem.media_type.setter
    def media_type(self, value: MediaType):
        MediaItem.media_type.fset(self, value)  # Call to the super method
        for season in self.seasons:
            season.media_type = value
        for file in self.files:
            file.media_type = value

    @MediaItem.metadata.setter
    def metadata(self, value: Metadata):
        MediaItem.metadata.fset(self, value)  # Call to the super method
        for file in self.files:
            file.metadata = deepcopy(value)
        for season in self.seasons:
            season.metadata = deepcopy(value)

    @property
    def new_name(self) -> str:
        if self.media_type == MediaType.ANIME:
            return self._parser.titlecase(f'{self.metadata.title}')
        return ''

    def rename(self):
        for f in self.files:
            f.rename()
        for s in self.seasons:
            s.rename()

        if not settings.MOCK_RENAME:
            os.rename(self.full_path, os.path.join(self.base_path, self.new_name))
        super(Show, self).rename()
