from environs import Env

env = Env()
env.read_env()

# Testing flags
ENABLE_PROFILE = True
LOG_HTTP = False
MOCK_RENAME = False

# Application configurations
MAL_CLIENT_ID = env.str('MAL_CLIENT_ID', '')
SIMILARITY_THRESHOLD = 0.9
