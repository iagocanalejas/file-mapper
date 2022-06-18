from src.core import MediaType
from src.models import Episode
from tests.media.mocks.episode import EpisodeMock
from tests.media.mocks.expected import ExpectedMediaItem, ExpectedEpisode, ExpectedSeason, EpisodeContainer, \
    SeasonContainer


def mock_anime_file(path: str = '', name: str = '') -> Episode:
    return Episode(base_path=path, item_name=name, _media_type=MediaType.ANIME)


__all__ = [
    EpisodeMock, mock_anime_file,
    ExpectedEpisode, ExpectedSeason,
    EpisodeContainer, SeasonContainer
]
