from environs import Env

env = Env()
env.read_env()

# Testing flags
ENABLE_PROFILE = True
LOG_HTTP = True
MOCK_RENAME = False

# Application configurations
MAL_CLIENT_ID = env.str('MAL_CLIENT_ID', '')
IMDB_API_KEY = env.str('IMDB_API_KEY', '')
SIMILARITY_THRESHOLD = 0.9
