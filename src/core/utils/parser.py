from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import ParsedInfo
from src.core.models import Season
from src.core.models import Show
from src.core.parsers import Parser


def parse_media_input(item: MediaItem, parser: Parser = None) -> MediaItem:
    parser = parser if parser is not None else Parser(media_type=item.media_type)
    media_title = parser.media_title(item)
    episode = episode_part = season = season_name = extension = None
    match item:
        case Episode():
            episode = parser.episode(item)
            episode_part = parser.episode_part(item)
            season = parser.season(item)
            season_name = parser.season_name(item)
            extension = parser.extension(item)
        case Season():
            assert isinstance(item, Season)
            [parse_media_input(e, parser=parser) for e in item.episodes]

            season = parser.season(item)
            season_name = parser.season_name(item)
        case Show():
            assert isinstance(item, Show)
            [parse_media_input(s, parser=parser) for s in item.seasons]

    item.parsed = ParsedInfo(
        episode=episode,
        episode_part=episode_part,
        season=season,
        season_name=season_name,
        media_title=media_title,
        extension=extension,
    )
    return item
