import factory

from src.core import models
from src.core.models import metadata
from src.core.types import Language
from src.tbuilder.models import Directory
from src.tbuilder.models import File
from src.tbuilder.models import Item


class AnimeMetadataFactory(factory.Factory):
    class Meta:
        model = metadata.AnimeMetadata

    datasource_data = {}
    title = factory.Sequence(lambda n: f'item_{n}')
    title_lang = Language.JA


class MediaItemFactory(factory.Factory):
    class Meta:
        model = models.MediaItem

    base_path = factory.Sequence(lambda n: f'/home/fake/{n}')
    parsed = None

    @classmethod
    def create(cls, **kwargs):
        if 'language' not in kwargs:
            kwargs['language'] = Language.JA
        obj = super().create(**kwargs)
        return obj


class EpisodeFactory(MediaItemFactory):
    class Meta:
        model = models.Episode


class SeasonFactory(MediaItemFactory):
    class Meta:
        model = models.Season


class ShowFactory(MediaItemFactory):
    class Meta:
        model = models.Show


class ItemFactory(factory.Factory):
    class Meta:
        model = Item

    base_path = factory.Sequence(lambda n: f'/home/fake/{n}')


class FileFactory(ItemFactory):
    class Meta:
        model = File


class DirectoryFactory(ItemFactory):
    class Meta:
        model = Directory
