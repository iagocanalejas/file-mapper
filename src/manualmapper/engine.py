import csv
import logging
import os
import re
from typing import List
from typing import Optional

import inquirer
from polyglot.text import Text

from src import runner
from src import settings
from src.core.matchers import AnimeTypeMatcher
from src.core.matchers import FilmTypeMatcher
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import ParsedInfo
from src.core.models import SubsFile
from src.core.parsers import Parser
from src.core.types import Language
from src.core.types import MediaType
from src.core.types import Object
from src.core.types import PathType
from src.core.types import SubtitleAction
from src.manualmapper.loader import load_media_item
from src.manualmapper.loader import load_subtitle_files
from src.manualmapper.logger import OutputLog
from src.manualmapper.processors import Processor
from src.manualmapper.processors import SubsProcessor

logger = logging.getLogger()

DEFAULT_MEDIA_TYPE = MediaType.ANIME
DEFAULT_PATH_TYPE = PathType.SHOW
DEFAULT_LANGUAGE = Language.JA


class Engine(Object):
    __item: MediaItem

    def __init__(self, path: str):
        """
        :param path: absolute path
        """
        assert os.path.isabs(path)

        self.__path = path
        self.__TYPE_MATCHERS = [AnimeTypeMatcher(), FilmTypeMatcher()]

    def run(self):
        self.__common_configuration()
        parser = Parser(media_type=runner.media_type)
        processor: Processor = Processor(media_type=runner.media_type)
        subtitles: Optional[SubsProcessor] = None

        self.__item = ParsedInfo.parse(load_media_item(self.__path, path_type=runner.path_type), parser)
        self.__item.media_type = runner.media_type

        # load and parse subtitle files if required
        subs: List[SubsFile] = []
        if runner.subs_acton:
            subtitles = SubsProcessor(media_type=MediaType.SUBS)
            subs = [ParsedInfo.parse(s, parser) for s in load_subtitle_files(self.__path)]
            subtitles.process(subs=subs, episodes=[e for e in self.__item.flatten() if isinstance(e, Episode)])

        # init the logger with the items we will be mapping
        [OutputLog().insert(id(i), i.path) for i in self.__item.flatten()]
        [OutputLog().insert(id(s), s.path) for s in subs]

        processor.process(item=self.__item)
        processor.post_process(item=self.__item)
        if runner.subs_acton and subtitles is not None:
            subtitles.post_process(subs=subs, action=runner.subs_acton)

        # log to file
        OutputLog().log(self.__item, to='output.csv')

    def undo(self, forced=False):
        path = self.__path if 'output.csv' in self.__path else os.path.join(self.__path, 'output.csv')
        with open(path) as file:
            reader = csv.reader(file, delimiter=',')
            for (original_name, new_name) in reader[1:]:
                if forced or inquirer.confirm(f'{new_name} -> {original_name}'):
                    os.rename(new_name, original_name)

    ########################
    #    Configuration     #
    ########################

    def __common_configuration(self):
        logger.debug(f'{self._class}:: running pre-configuration')

        answers = inquirer.prompt([
            inquirer.List(
                name='path_type',
                message='Path type',
                choices=PathType.__members__.keys(),
                default=self.__path_type().name
            ),
            inquirer.List(
                name='media_type',
                message='Input media type',
                choices=[m for m in MediaType.__members__.keys() if m != MediaType.UNKNOWN.name],
                default=self.__media_type(os.path.basename(self.__path)).name
            ),
            inquirer.List(
                name='language',
                message='Language',
                choices=Language.__members__.keys(),
                default=self.__language(os.path.basename(self.__path)).name
            ),
            inquirer.List(
                name='subs',
                message='How to handle subs files',
                choices=list(SubtitleAction.__members__.keys()) + ['NONE'],
                default='NONE'
            ),
        ])

        runner.media_type = MediaType[answers['media_type']]
        runner.path_type = PathType[answers['path_type']]
        runner.language = Language[answers['language']]
        runner.subs_acton = SubtitleAction[answers['subs']] if answers['subs'] != 'NONE' else None

        logger.debug(f'{self._class}:: running with configuration::{settings}')

    ########################
    #    Default Config    #
    ########################

    def __language(self, item_name: str) -> Language:
        lang = Text(item_name).language.code
        lang = lang if lang in Language.__members__.values() else DEFAULT_LANGUAGE.value

        logger.debug(f'{self._class}:: {item_name} :: using language :: {lang}')
        return Language[lang.upper()]

    def __media_type(self, item_name: str) -> MediaType:
        try:
            match = next(tm for tm in self.__TYPE_MATCHERS if tm.matches(item_name))
        except StopIteration:
            return DEFAULT_MEDIA_TYPE
        else:
            return match.media_type if match else DEFAULT_MEDIA_TYPE

    def __path_type(self) -> PathType:
        item_name, path = os.path.basename(self.__path), self.__path
        if os.path.isfile(path):
            if re.match(r'^.* ova.*$|^.* special.*$', item_name, re.IGNORECASE) is not None:
                return PathType.OVA
            return PathType.EPISODE

        if all(os.path.isfile(os.path.join(path, n)) for n in os.listdir(path)):
            return PathType.SEASON

        return DEFAULT_PATH_TYPE
