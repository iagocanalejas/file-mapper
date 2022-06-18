import logging
from os.path import basename

from src.core import MediaType
from src.models import Season, Directory, Show, File
from src.parsers import Parser
from src.processors import Processor

logger = logging.getLogger()


class Engine(object):
    preset_media_type: MediaType = None

    def handle_file(self, file: File):
        logger.info(f'{basename(__file__)}:: working on :: \'{file.base_path}\'')
        logger.info(f'{basename(__file__)}:: with file :: \'{file.item_name}\'')

        episode = file.to_episode()
        processor = Processor(parser=Parser(file.item_name, media_type=self.preset_media_type))
        processor.process_episode(episode)

        episode.rename()

    def handle_directory(self, directory: Directory):
        logger.info(f'{basename(__file__)}:: working on :: \'{directory.base_path}\'')
        logger.info(f'{basename(__file__)}:: with directory :: \'{directory.item_name}\'')

        # Check for show
        if directory.is_show_folder:
            self.__handle_show(directory.to_show())
            return

            # Check for season
        if directory.is_season_folder:
            # If we only have files or files and a sub folder we assume we are in a season
            self.__handle_season(directory.to_season())
            return

        # Handle independent files
        [self.handle_file(item) for item in directory.items if isinstance(item, File)]

    def __handle_season(self, season: Season):
        parser = Parser(season.item_name, media_type=self.preset_media_type, match_extension=False)
        if parser.media_type == MediaType.UNKNOWN and len(season.episodes) > 0:
            parser = Parser(season.episodes[0].item_name, media_type=self.preset_media_type)

        processor = Processor(parser=parser)
        processor.process_season(season)

        season.rename()

    def __handle_show(self, show: Show):
        parser = Parser(show.item_name, media_type=self.preset_media_type, match_extension=False)
        if parser.media_type == MediaType.UNKNOWN and len(show.seasons) > 0:
            parser = Parser(show.seasons[0].item_name, media_type=self.preset_media_type)
        if parser.media_type == MediaType.UNKNOWN and len(show.files) > 0:
            parser = Parser(show.files[0].item_name, media_type=self.preset_media_type)

        processor = Processor(parser=parser)
        processor.process_show(show)

        show.rename()
