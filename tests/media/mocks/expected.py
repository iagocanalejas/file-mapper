import os
from dataclasses import dataclass
from typing import List

from src.models import Episode, Season
from src.models.metadata import AnimeMetadata


@dataclass
class ExpectedMediaItem:
    media_name: str
    new_name: str


@dataclass
class ExpectedEpisode(ExpectedMediaItem):
    media_name: str
    new_name: str
    season: int
    episode: int
    extension: str


@dataclass
class ExpectedSeason(ExpectedMediaItem):
    season: int


class EpisodeContainer:
    episode: Episode
    expected: ExpectedEpisode

    def __init__(self, item_name: str, title: str, episode_name: str, expected: ExpectedEpisode):
        self.episode = Episode(
            base_path=os.path.abspath(__file__),
            item_name=item_name,
            _metadata=AnimeMetadata(
                mal_id=37403,
                title=title,
                media_type='tv',
                episode_name=episode_name,
                alternative_titles={'en': '', 'ja': 'あひるの空', 'synonyms': []},
            ),
        )
        self.expected = expected


class SeasonContainer:
    season: Season
    expected: ExpectedSeason

    def __init__(self, item_name: str, title: str, episodes: List[Episode], expected: ExpectedSeason):
        self.season = Season(
            base_path=os.path.abspath(__file__),
            item_name=item_name,
            episodes=episodes,
            _metadata=AnimeMetadata(
                mal_id=37403,
                title=title,
                media_type='tv',
                alternative_titles={'en': '', 'ja': 'あひるの空', 'synonyms': []},
            ),
        )
        self.expected = expected
