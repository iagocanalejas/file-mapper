import argparse
import logging
import os
import sys

from src import settings
from src.core.models.config import GlobalConfig
from src.core.types import Language
from src.engine import Engine
from src.matchers import MediaType

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main(path: str, media_type: str, lang: str):
    if not os.path.exists(path):
        raise ValueError(f'\'{path}\' does not exist')

    engine = Engine(path=path, media_type=media_type, language=lang)
    engine.run()


def __parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path to be handled')
    parser.add_argument('--type', default=None, help=f'Preset type to be used. Valid: {MediaType.__members__.keys()}')
    parser.add_argument('--lang', default=None,
                        help=f'Preset language to be used. Valid: {Language.__members__.values()}')
    parser.add_argument('--wikipedia', default=None, type=str,
                        help=f'Predefined Wikipedia URL')
    parser.add_argument('--prefill', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    return parser.parse_args()


def __parse_global_datasource(parsed_args):
    if parsed_args.wikipedia:
        GlobalConfig().wikipedia_url = parsed_args.wikipedia


def __prefill():
    namespace = argparse.Namespace()

    wikipedia = input('\nPrefill wikipedia URL: ')
    if wikipedia:
        setattr(namespace, 'wikipedia', wikipedia)

    __parse_global_datasource(namespace)


if __name__ == '__main__':
    args = __parse_arguments()
    logger.info(f'{os.path.basename(__file__)}:: args -> {args.__dict__}')

    if args.debug:
        settings.MOCK_RENAME = True

    if args.prefill:
        __prefill()

    __parse_global_datasource(args)

    if settings.ENABLE_PROFILE:
        import cProfile
        import pstats

        with cProfile.Profile() as pr:
            main(os.path.abspath(args.path), args.type, args.lang)

        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats(filename='profiling.prof')
    else:
        main(os.path.abspath(args.path), args.type, args.lang)
