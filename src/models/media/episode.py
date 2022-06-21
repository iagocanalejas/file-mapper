import os
from dataclasses import dataclass

import settings
from src.core import MediaType
from src.core.exceptions import UnsupportedMediaType
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
            assert isinstance(self._metadata, AnimeMetadata)
            return self._metadata.episode_name

        raise UnsupportedMediaType(f'{self}')

    @property
    def extension(self) -> str:
        return self._parser.extension(self.item_name)

    @property
    def new_name(self) -> str:
        if self.media_type == MediaType.ANIME:
            assert isinstance(self._metadata, AnimeMetadata)

            title = self._parser.titlecase(self._metadata.title.replace('Season ', 'S'))
            episode_name = self._parser.titlecase(self._metadata.episode_name)
            return f'{title} - {self.episode:02d} - {episode_name}.{self.extension}'

        raise UnsupportedMediaType(f'{self}')

    def rename(self):
        if not settings.MOCK_RENAME:
            os.rename(self.full_path, os.path.join(self.base_path, self.new_name))

        super(Episode, self).rename()
