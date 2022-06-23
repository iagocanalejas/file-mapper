import logging
import os
from typing import Optional, List

from src.core.exceptions import UnsupportedMediaType
from src.core.models import Season, Show, Episode
from src.core.types import Object
from src.processors import Processor
from src.tbuilder import Tree
from src.tbuilder.models import File, Directory
from src.matchers import MediaType, TypeMatcher, AnimeTypeMatcher, FilmTypeMatcher

logger = logging.getLogger()


class Engine(Object):
    _preset_media_type: MediaType = None
    _type_matchers: List[TypeMatcher] = [AnimeTypeMatcher(), FilmTypeMatcher()]
    _tree: Tree

    def __init__(self, path: str, media_type: Optional[str] = None):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if media_type is not None:
            try:
                self._preset_media_type = MediaType[media_type.upper()]
            except KeyError:
                raise UnsupportedMediaType(media_type)

        self._tree = Tree(path=path)

    def handle_file(self, file: File = None):
        logger.info(f'{self._class}:: working on :: \'{self._tree.path}\'')
        logger.info(f'{self._class}:: with file :: \'{self._tree.name}\'')

        if file is None:
            file = self._tree.root
        if not file.is_valid:
            raise ValueError(f'invalid file {file}')
        assert isinstance(file, File)

        episode = Episode.from_file(file=file, media_type=self.__media_type(to_match=file.name))
        processor = Processor(media_type=episode.media_type)
        processor.process_episode(episode)

    def handle_directory(self, directory: Directory = None):
        logger.info(f'{self._class}:: working on :: \'{self._tree.path}\'')
        logger.info(f'{self._class}:: with directory :: \'{self._tree.name}\'')

        if directory is None:
            directory = self._tree.root
        if not directory.is_valid:
            raise ValueError(f'invalid directory {directory}')
        assert isinstance(directory, Directory)

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
            show = Show.from_directory(directory=directory, media_type=self.__media_type())
            processor = Processor(media_type=show.media_type)
            processor.process_show(show)
            return

            # Check for season
        if directory.can_be_season:
            # If we only have files or files and a sub folder we assume we are in a season
            season = Season.from_directory(directory=directory, media_type=self.__media_type())
            processor = Processor(media_type=season.media_type)
            processor.process_season(season)
            return

        # Handle independent files
        [self.handle_file(item) for item in directory.childs if isinstance(item, File) and item.is_valid]

    def run(self):
        if self._tree.is_file:
            self.handle_file()
        if self._tree.is_directory:
            self.handle_directory()

    def __media_type(self, to_match: str = None) -> MediaType:
        if self._preset_media_type is not None:
            return self._preset_media_type

        if to_match is None:
            to_match = self._tree.name

        match = next(tm for tm in self._type_matchers if tm.matches(to_match))
        return match.media_type if match else MediaType.UNKNOWN
