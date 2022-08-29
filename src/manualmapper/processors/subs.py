import logging
import os.path
from typing import List

import inquirer

from src import runner
from src.core.models import Episode
from src.core.models import SubsFile
from src.core.types import MediaType
from src.core.types import SubtitleAction
from src.manualmapper.processors import Processor

logger = logging.getLogger()


class SubsProcessor(Processor, media_type=MediaType.SUBS):
    _instance = None

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def process(self, subs: List[SubsFile], episodes: List[Episode], **kwargs):
        [s.update('parent', next(self.__can_match(e, s) for e in episodes)) for s in subs]

        while any(s.parent is None for s in subs):
            todo = inquirer.list_input(
                message='Unmatched subtitle files found. What to do with them?',
                choices=['SHOW', 'MANUAL MATCH', 'IGNORE'],
            )
            match todo:
                case 'SHOW':
                    [logger.info(f'{s.item_name}') for s in subs if s.parent is None]
                case 'MANUAL MATCH':
                    selected_item = inquirer.list_input(
                        message='Element to match',
                        choices=[f'{s.item_name}' for s in subs if s.parent is None],
                    )
                    selected_item = next(s for s in subs if s.item_name == selected_item)
                    self.__manual_match(selected_item, episodes)
                case 'IGNORE':
                    break

    def post_process(self, subs: List[SubsFile], action: SubtitleAction, **kwargs):
        # parent processor.post_process should be called by this point as this will use parent's name
        match action:
            case SubtitleAction.RENAME:
                [s.rename(self.formatter.new_name(s)) for s in subs]
            case _:
                raise NotImplementedError

    @staticmethod
    def __manual_match(item: SubsFile, episodes: List[Episode]):
        selected_item = inquirer.list_input(
            message=f'Parent item for {item.item_name}',
            choices=[f'{e.item_name}' for e in episodes] + ['None'],
        )
        item.parent = next(e for e in episodes if selected_item != 'None' and e.item_name == selected_item)

    @staticmethod
    def __can_match(episode: Episode, sub_file: SubsFile) -> bool:
        return (
                episode.parsed.episode == sub_file.parsed.episode
                and episode.parsed.episode_part == sub_file.parsed.episode_part
                and episode.parsed.season == sub_file.parsed.season
        )
