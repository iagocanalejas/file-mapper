import logging
import os
from typing import List
from typing import Optional

from polyglot.text import Text

from src.core.exceptions import UnsupportedMediaType
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import ParsedInfo
from src.core.models import Season
from src.core.models import Show
from src.core.models.config import GlobalConfig
from src.core.types import Language
from src.core.types import Object
from src.matchers import AnimeTypeMatcher
from src.matchers import FilmTypeMatcher
from src.matchers import MediaType
from src.matchers import TypeMatcher
from src.parsers import Parser
from src.processors import Processor
from src.tbuilder import Tree
from src.tbuilder.models import Directory
from src.tbuilder.models import File

logger = logging.getLogger()


class Engine(Object):
    _tree: Tree
    __TYPE_MATCHERS: List[TypeMatcher] = [AnimeTypeMatcher(), FilmTypeMatcher()]

    def __init__(self, path: str, media_type: Optional[str] = None, language: Optional[str] = None):
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        try:
            GlobalConfig(
                media_type=MediaType[media_type.upper()] if media_type else None,
                language=Language[language.upper()] if language else None,
            )
        except KeyError as ke:
            raise UnsupportedMediaType(ke)

        self._tree = Tree(path=path)

    def run(self):
        if self._tree.is_file:
            self.handle_file()
        if self._tree.is_directory:
            self.handle_directory()

    def handle_file(self, file: File = None):
        logger.info(f'{self._class}:: working on :: \'{self._tree.path}\'')
        logger.info(f'{self._class}:: with file :: \'{self._tree.name}\'')

        file = file if file is not None else self._tree.root
        assert isinstance(file, File), f'invalid file {file}'
        assert file.is_valid, f'invalid file {file}'

        episode = Episode.from_file(file=file)
        episode.media_type = self.__categorize(episode)
        episode.language = self.__language(episode)
        parse_input(episode)

        processor = Processor(media_type=episode.media_type)
        processor.process_episode(episode)

    def handle_directory(self, directory: Directory = None):
        logger.info(f'{self._class}:: working on :: \'{self._tree.path}\'')
        logger.info(f'{self._class}:: with directory :: \'{self._tree.name}\'')

        directory = directory if directory is not None else self._tree.root
        assert isinstance(directory, Directory), f'invalid directory {directory}'
        assert directory.is_valid, f'invalid directory {directory}'

        if len(directory.childs) == 1:
            lonely_item = directory.childs[0]
            if isinstance(lonely_item, File):
                self.handle_file(lonely_item)
            else:
                assert isinstance(lonely_item, Directory)
                self.handle_directory(lonely_item)
            return

        # Check for show
        if directory.can_be_show:
            show = Show.from_directory(directory=directory)
            show.media_type = self.__categorize(show)
            show.language = self.__language(show)
            parse_input(show)

            processor = Processor(media_type=show.media_type)
            processor.process_show(show)
            return

            # Check for season
        if directory.can_be_season:
            # If we only have files or files and a sub folder we assume we are in a season
            season = Season.from_directory(directory=directory)
            season.media_type = self.__categorize(season)
            season.language = self.__language(season)
            parse_input(season)

            processor = Processor(media_type=season.media_type)
            processor.process_season(season)
            return

        # Handle independent files
        logger.info(f'{self._class}:: as separated files')
        [self.handle_file(item) for item in directory.childs if isinstance(item, File) and item.is_valid]
        [self.handle_directory(item) for item in directory.childs if isinstance(item, Directory) and item.is_valid]

    def __categorize(self, item: MediaItem) -> MediaType:
        if GlobalConfig().media_type is not None:
            return GlobalConfig().media_type

        match = next(tm for tm in self.__TYPE_MATCHERS if tm.matches(item.item_name))
        return match.media_type if match else MediaType.UNKNOWN

    def __language(self, item: MediaItem) -> Language:
        if GlobalConfig().language is not None:
            logger.info(f'{self._class}:: {item.item_name} :: using language :: {GlobalConfig().language}')
            return GlobalConfig().language

        lang = Text(item.item_name).language.code
        lang = lang if lang in Language.__members__.values() else Language.JA.value

        logger.info(f'{self._class}:: {item.item_name} :: using language :: {lang}')
        return Language[lang.upper()]


def parse_input(item: MediaItem, parser: Parser = None):
    parser = Parser(media_type=item.media_type) if parser is None else parser
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
            [parse_input(e, parser=parser) for e in item.episodes]

            season = parser.season(item)
            season_name = parser.season_name(item)
        case Show():
            assert isinstance(item, Show)
            [parse_input(e, parser=parser) for e in item.episodes]
            [parse_input(s, parser=parser) for s in item.seasons]

    item.parsed = ParsedInfo(
        episode=episode,
        episode_part=episode_part,
        season=season,
        season_name=season_name,
        media_title=media_title,
        extension=extension,
    )
