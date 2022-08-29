import logging
import re

import inquirer

from src import runner
from src.core.models import Episode
from src.core.models import MediaItem
from src.core.models import Season
from src.core.models import Show
from src.core.models.metadata import as_anime
from src.core.types import MediaType
from src.core.types import PathType
from src.filemapper.datasources.api import MalAPI
from src.filemapper.datasources.scrapper import WikipediaScrapper
from src.manualmapper.processors import Processor

logger = logging.getLogger()


class AnimeProcessor(Processor, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **_):
        self.__mal_api = MalAPI()
        self.__wikipedia_scrapper = WikipediaScrapper()

    def process(self, item: MediaItem, **kwargs):
        mal_name = inquirer.text(message='MyAnimeList Name', default=item.parsed.media_title)
        runner.mal_url = f'https://api.myanimelist.net/v2/anime?q={mal_name}&fields=alternative_titles'

        item.metadata = self.__retrieve_mal_metadata()
        logger.info(f'Selected anime {item.metadata.title}')

        wikipedia = inquirer.text('Wikipedia URL', validate=lambda _, x: WikipediaScrapper.check_url(x))
        runner.wikipedia_url = wikipedia
        self.__fill_wikipedia_metadata(item)

    def post_process(self, item: MediaItem):
        while True:
            menu = inquirer.list_input(
                message='What to do',
                choices=['Preview', 'Manual Edit', 'Rename Selection', 'Rename All', 'Cancel'],
            )
            match menu.lower():
                case 'preview':
                    [
                        logger.info(f'{i._class}:: {i.item_name} -> {self.formatter.new_name(i)}')
                        for i in item.flatten()
                    ]
                case 'manual edit':
                    renaming_element = inquirer.list_input(
                        message='Element to edit',
                        choices=[
                            f'{i._class}:: {i.item_name} -> {self.formatter.new_name(i)}'
                            for i in item.flatten()
                        ],
                    )
                    selected_item = renaming_element.split(':: ')[1].split(' -> ')[0]
                    selected_item = next(i for i in item.flatten() if i.item_name == selected_item)
                    self.__edit(selected_item)
                case 'rename selection':
                    renaming_list = inquirer.checkbox(
                        message='Files to rename',
                        choices=[
                            f'{i._class}:: {i.item_name} -> {self.formatter.new_name(i)}'
                            for i in item.flatten()
                        ]
                    )
                    selected = [i.split(':: ')[1].split(' -> ')[0] for i in renaming_list]
                    [i.rename(self.formatter.new_name(i)) for i in item.flatten()[::-1] if i.item_name in selected]
                    break
                case 'rename all':
                    [i.rename(self.formatter.new_name(i)) for i in item.flatten()[::-1]]
                    break
                case 'cancel':
                    break

    def __retrieve_mal_metadata(self):
        matched_options = self.__mal_api.options(runner.mal_url)
        choices = [o.title for o in matched_options] + ['None']
        chosen_name = inquirer.list_input('Choose the correct option', choices=choices)

        if chosen_name == 'None':
            mal_id = inquirer.text('MyAnimeList Anime Id', validate=lambda _, x: re.match(r'\d+', x))
            return self.__mal_api.anime_by_id(mal_id=mal_id)
        else:
            return next(m for m in matched_options if m.title == chosen_name)

    def __fill_wikipedia_metadata(self, item: MediaItem):
        match runner.path_type:
            case PathType.SHOW:
                assert isinstance(item, Show)
                self.__wikipedia_scrapper.fill_show_names(item)
            case PathType.SEASON:
                assert isinstance(item, Season)
                self.__wikipedia_scrapper.fill_season_names(item)
            case PathType.EPISODE:
                assert isinstance(item, Episode)
                self.__wikipedia_scrapper.fill_episode_name(item)

    @staticmethod
    def __edit(item: MediaItem):
        match item:
            case Show():
                answers = inquirer.prompt([
                    inquirer.Text(
                        name='show_name',
                        message=f'Rename show {as_anime(item.metadata).title} to:'
                    ),
                    inquirer.Text(
                        name='show_name_lang',
                        message=f'Change language {as_anime(item.metadata).title_lang} to:'
                    ),
                ])
                if answers['show_name']:
                    item.update('title', answers['show_name'])
                if answers['show_name_lang']:
                    item.update('title_lang', answers['show_name_lang'])
            case Season():
                season_name = inquirer.text(f'Rename season {as_anime(item.metadata).season_name} to:')
                if season_name:
                    item.update('season_name', season_name)
            case Episode():
                episode_name = inquirer.text(f'Rename episode {as_anime(item.metadata).episode_name} to:')
                if episode_name:
                    item.update('episode_name', episode_name)
