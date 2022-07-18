import factory

from src.core import models
from src.core.models import metadata
from src.core.types import DatasourceName
from src.core.types import Language


class AnimeMetadataFactory(factory.Factory):
    class Meta:
        model = metadata.AnimeMetadata

    datasource_id = factory.Sequence(lambda n: n)
    datasource = DatasourceName.MAL,
    title = factory.Sequence(lambda n: f'item_{n}')
    alternative_titles = {}


class MediaItemFactory(factory.Factory):
    class Meta:
        model = models.MediaItem

    base_path = factory.Sequence(lambda n: f'/home/fake/{n}')

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
