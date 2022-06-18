import os
from dataclasses import dataclass

import settings
from src.core import MediaType
from src.models.item import MediaItem
from src.models.metadata import AnimeMetadata


@dataclass
class Episode(MediaItem):
    @staticmethod
    def is_valid_file(name: str) -> bool:
        return Episode._parser.extension(name) != 'txt' and Episode._parser.extension(name) != 'exe'

    @property
    def season(self) -> int:
        return self._parser.season(self.item_name)

    @property
    def episode(self) -> int:
        return self._parser.episode(self.item_name)

    @property
    def episode_name(self) -> str:
        if self.media_type == MediaType.ANIME:
            metadata: AnimeMetadata = self.metadata  # We know metadata is an AnimeMetadata for ANIME
            return metadata.episode_name

        raise NotImplementedError(f'{self}:: unsupported media type {self.media_type}')

    @property
    def extension(self) -> str:
        return self._parser.extension(self.item_name)

    @property
    def new_name(self) -> str:
        if self.media_type == MediaType.ANIME:
            metadata: AnimeMetadata = self.metadata  # We know metadata is an AnimeMetadata for ANIME
            title = metadata.title.replace('Season ', 'S')
            return f'{self._parser.titlecase(title)} - {self.episode:02d} - {self._parser.titlecase(metadata.episode_name)}.{self.extension}'

        raise NotImplementedError(f'{self}:: unsupported media type {self.media_type}')

    def rename(self):
        if not settings.MOCK_RENAME:
            os.rename(self.full_path, os.path.join(self.base_path, self.new_name))

        super(Episode, self).rename()
