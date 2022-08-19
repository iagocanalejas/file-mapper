from environs import Env

from src.core.types import DatasourceName

env = Env()
env.read_env()

# Testing flags
DEBUG = False
ENABLE_PROFILE = False

# Application configurations
MAL_CLIENT_ID = env.str('MAL_CLIENT_ID', '')
IMDB_API_KEY = env.str('IMDB_API_KEY', '')
SIMILARITY_THRESHOLD = 0.9

DATASOURCE_WEIGHT = {
    DatasourceName.MAL: 100,
    DatasourceName.ANILIST: 50,
    DatasourceName.IMDB: 10,
}
