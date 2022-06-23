import factory

from src.core import models
from src.core.models import metadata


class MetadataFactory(factory.Factory):
    class Meta:
        model = metadata.Metadata

    title = factory.Sequence(lambda n: f"item_{n}")


class AnimeMetadataFactory(factory.Factory):
    class Meta:
        model = metadata.AnimeMetadata

    mal_id = factory.Sequence(lambda n: n)
    media_type = 'tv'
    title = factory.Sequence(lambda n: f"item_{n}")
    alternative_titles = {}


class MediaItemFactory(factory.Factory):
    class Meta:
        model = models.MediaItem

    base_path = factory.Sequence(lambda n: f"/home/fake/{n}")
    item_name = factory.Sequence(lambda n: f"item_{n}.mkv")
    _metadata = factory.SubFactory(AnimeMetadataFactory)


class EpisodeFactory(MediaItemFactory):
    class Meta:
        model = models.Episode


class SeasonFactory(MediaItemFactory):
    class Meta:
        model = models.Season

    class Params:
        number_of_episodes = 0

    episodes = factory.LazyAttribute(lambda self: [EpisodeFactory()] * self.number_of_episodes)


class ShowFactory(MediaItemFactory):
    class Meta:
        model = models.Show

    class Params:
        number_of_episodes = 0
        number_of_seasons = 0

    episodes = factory.LazyAttribute(lambda self: [EpisodeFactory()] * self.number_of_episodes)
    seasons = factory.LazyAttribute(
        lambda self: [SeasonFactory(number_of_episodes=self.number_of_episodes)] * self.number_of_seasons
    )
