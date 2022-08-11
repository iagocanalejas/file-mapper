import logging
import os
import re
from dataclasses import dataclass
from typing import Optional

import inquirer
from polyglot.text import Text

from src.core import GlobalConfig
from src.core.formatter import Formatter
from src.core.matchers import AnimeTypeMatcher
from src.core.matchers import FilmTypeMatcher
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.models.metadata import AnimeMetadata
from src.core.parsers import Parser
from src.core.types import Language
from src.core.types import MediaType
from src.core.types import Object
from src.core.types import PathType
from src.core.utils.parser import parse_media_input
from src.filemapper.datasources.api import MalAPI
from src.filemapper.datasources.scrapper import WikipediaScrapper
from src.manualmapper.loader import load_media_item

logger = logging.getLogger()

DEFAULT_MEDIA_TYPE = MediaType.ANIME
DEFAULT_PATH_TYPE = PathType.SHOW
DEFAULT_LANGUAGE = Language.JA


@dataclass
class _EngineConfig:
    path_type: Optional[PathType] = None

    def __str__(self):
        return f"""\n\tpath_type: {self.path_type}"""


class Engine(Object):
    __config: _EngineConfig
    __item: MediaItem
    __formatter: Formatter

    def __init__(self, path: str):
        """
        :param path: absolute path
        """
        assert os.path.isabs(path)

        self.__path = path
        self.__config = _EngineConfig()
        self.__TYPE_MATCHERS = [AnimeTypeMatcher(), FilmTypeMatcher()]

    def run(self):
        self.__common_configuration()

        self.__item = parse_media_input(
            load_media_item(self.__path, path_type=self.__config.path_type),
            parser=Parser(media_type=GlobalConfig().media_type)
        )
        self.__item.media_type = GlobalConfig().media_type
        self.__formatter = Formatter(media_type=GlobalConfig().media_type)

        match GlobalConfig().media_type:
            case MediaType.ANIME:
                self.__anime_configuration()
                self.__process_anime()

    ########################
    #    Configuration     #
    ########################

    def __common_configuration(self):
        logger.info(f'{self._class}:: running pre-configuration')

        answers = inquirer.prompt([
            inquirer.List(
                name='path_type',
                message='Path type',
                choices=PathType.__members__.keys(),
                default=DEFAULT_PATH_TYPE.name
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
        ])

        GlobalConfig().media_type = MediaType[answers['media_type']]
        GlobalConfig().language = Language[answers['language']]

        self.__config.path_type = PathType[answers['path_type']]

        logger.info(f'{self._class}:: running with configuration::{GlobalConfig()}')
        logger.info(f'{self._class}:: running with local configuration::{self.__config}')

    def __anime_configuration(self):
        logger.info(f'{self._class}:: configuring {MediaType.ANIME}')

        answers = inquirer.prompt([
            inquirer.Text(
                name='mal',
                message='MyAnimeList Name',
                default=self.__item.parsed.media_title
            ),
            inquirer.Text(
                name='wikipedia',
                message='Wikipedia URL',
                validate=lambda _, x: WikipediaScrapper.check_url(x)
            ),
        ])

        GlobalConfig().mal_url = f'https://api.myanimelist.net/v2/anime?q={answers["mal"]}&fields=alternative_titles'
        GlobalConfig().wikipedia_url = answers['wikipedia']

        logger.info(f'{self._class}:: running with configuration::{GlobalConfig()}')
        logger.info(f'{self._class}:: running with local configuration::{self.__config}')

    ########################
    #      Processing      #
    ########################

    def __process_anime(self):
        mal = MalAPI()
        matched_options = mal.options(GlobalConfig().mal_url)
        choices = ['None'] + [o.title for o in matched_options]
        answers = inquirer.prompt([
            inquirer.List(
                name='chosen_name',
                message='Choose the correct option',
                choices=choices,
            ),
        ])

        self.__item.metadata = self.__manual_anime_input(mal) \
            if answers['chosen_name'] == 'None' \
            else next(m for m in matched_options if m.title == answers['chosen_name'])

        print(f'Selected anime {self.__item.metadata.title}')

        wikipedia = WikipediaScrapper()
        match self.__config.path_type:
            case PathType.SHOW:
                assert isinstance(self.__item, Show)
                wikipedia.fill_show_names(self.__item)
            case PathType.SEASON:
                assert isinstance(self.__item, Season)
                wikipedia.fill_season_names(self.__item)
            case PathType.EPISODE:
                assert isinstance(self.__item, Episode)
                wikipedia.fill_episode_name(self.__item)

        while True:
            menu = inquirer.prompt([
                inquirer.List(
                    name='chosen_menu',
                    message='What to do',
                    choices=['Preview', 'Rename Selection', 'Rename All', 'Cancel'],
                ),
            ])
            match menu['chosen_menu'].lower():
                case 'preview':
                    print([
                        f'{i._class}:: {i.item_name} -> {self.__formatter.new_name(i)}\n'
                        for i in self.__item.flatten()
                    ])
                case 'rename selection':
                    answers = inquirer.prompt([
                        inquirer.Checkbox(
                            name='renaming_list',
                            message='Files to rename',
                            choices=[
                                f'{i._class}:: {i.item_name} -> {self.__formatter.new_name(i)}'
                                for i in self.__item.flatten()
                            ]
                        ),
                    ])
                    selected_titles = [i.split(':: ')[1].split(' -> ')[0] for i in answers['renaming_list']]
                    [self.__rename(i) for i in self.__item.flatten() if i.item_name in selected_titles]
                    break
                case 'rename all':
                    [self.__rename(i) for i in self.__item.flatten()]
                    break
                case 'cancel':
                    break

    ########################
    #    Default Config    #
    ########################

    def __language(self, item_name: str) -> Language:
        lang = Text(item_name).language.code
        lang = lang if lang in Language.__members__.values() else DEFAULT_LANGUAGE.value

        logger.info(f'{self._class}:: {item_name} :: using language :: {lang}')
        return Language[lang.upper()]

    def __media_type(self, item_name: str) -> MediaType:
        try:
            match = next(tm for tm in self.__TYPE_MATCHERS if tm.matches(item_name))
        except StopIteration:
            return DEFAULT_MEDIA_TYPE
        else:
            return match.media_type if match else DEFAULT_MEDIA_TYPE

    ########################
    #         Utils        #
    ########################

    @staticmethod
    def __manual_anime_input(mal: MalAPI) -> AnimeMetadata:
        answers = inquirer.prompt([
            inquirer.Text(
                name='mal_id',
                message='MyAnimeList Anime Id',
                validate=lambda _, x: re.match(r'\d+', x)
            ),
        ])
        return mal.anime_by_id(mal_id=answers['mal_id'])

    def __rename(self, item: MediaItem):
        item.item_name = self.__formatter.new_name(item)
        os.rename(item.path, os.path.join(item.base_path, item.item_name))
