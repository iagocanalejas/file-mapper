import argparse
import itertools
import logging
import os
import sys
from typing import List

import settings
from src.engine import Engine
from src.models import File, Directory
from src.core import MediaType

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

engine: Engine = Engine()


def main(path: str, media_type: str):
    if not os.path.exists(path):
        raise ValueError(f'\'{path}\' does not exist')

    if media_type is not None:
        engine.preset_media_type = MediaType[media_type.upper()]

    if os.path.isfile(path):
        file = File(base_path=os.path.dirname(path), item_name=os.path.basename(path))
        engine.handle_file(file)
    else:
        engine.handle_directory(__build_tree(path))
        return


def __build_tree(path: str, depth: int = 0) -> Directory:
    root = Directory(base_path=os.path.dirname(path), item_name=os.path.basename(path), depth=depth)
    files: List[File] = []
    directories: List[Directory] = []

    for item in os.listdir(root.full_path):
        full_path = os.path.join(root.full_path, item)
        if os.path.isfile(full_path):
            files.append(File(path, item))
        else:
            directories.append(__build_tree(full_path, depth=depth + 1))

    root.items = list(itertools.chain(directories, files))
    return root


def __parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help='Path to be handled')
    parser.add_argument("--type", default=None, help=f'Known type for the path {MediaType.__members__.keys()}')
    parser.add_argument("--debug", action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = __parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    if args.debug:
        settings.MOCK_RENAME = True

    if settings.ENABLE_PROFILE:
        import cProfile
        import pstats

        with cProfile.Profile() as pr:
            main(os.path.abspath(args.path), args.type)

        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats(filename='profiling.prof')
    else:
        main(os.path.abspath(args.path), args.type)
