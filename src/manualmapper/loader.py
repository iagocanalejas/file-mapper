import os

from src.core import GlobalConfig
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.types import PathType


def load_media_item(path: str, path_type: PathType) -> MediaItem:
    match path_type:
        case PathType.SHOW:
            return __build_show(path)
        case PathType.SEASON:
            return __build_season(path)
        case PathType.EPISODE:
            return __build_episode(path)


def __build_show(path: str) -> Show:
    show = Show(
        base_path=os.path.dirname(path),
        item_name=os.path.basename(path),
        language=GlobalConfig().language,
        parsed=None,
    )

    # assume all sub_folders are seasons
    sub_folders = [os.path.join(path, sp) for sp in os.listdir(path) if os.path.isdir(os.path.join(path, sp))]

    # TODO: handle files
    files = [os.path.join(path, sp) for sp in os.listdir(path) if os.path.isfile(os.path.join(path, sp))]

    show.seasons = [
        __build_season(p, show=show) for p in sub_folders
    ]

    return show


def __build_season(path: str, show: Show = None) -> Season:
    season = Season(
        base_path=os.path.dirname(path),
        item_name=os.path.basename(path),
        show=show,
        language=GlobalConfig().language,
        parsed=None,
    )

    # TODO: handle sub_folders (subs)
    sub_folders = [os.path.join(path, sp) for sp in os.listdir(path) if os.path.isdir(os.path.join(path, sp))]

    # assume all files are episodes
    episodes = [os.path.join(path, sp) for sp in os.listdir(path) if os.path.isfile(os.path.join(path, sp))]

    season.episodes = [
        __build_episode(p, season=season, show=show) for p in episodes
    ]

    return season


def __build_episode(path: str, season: Season = None, show: Show = None) -> Episode:
    return Episode(
        base_path=os.path.dirname(path),
        item_name=os.path.basename(path),
        season=season,
        show=show,
        language=GlobalConfig().language,
        parsed=None,
    )