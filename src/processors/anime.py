from src.core import MediaType
from src.datasources.api import MalAPI
from src.datasources.scrapper import WikipediaScrapper
from src.models import Show, Season, Episode
from src.processors import Processor


class AnimeProcessor(Processor, media_type=MediaType.ANIME):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def process_episode(self, episode: Episode):
        super(AnimeProcessor, self).process_episode(episode)

        finder = MalAPI()
        episode.metadata = finder.get_anime_details(anime_id=finder.find_anime(finder.build_search_keyword(episode)))

        WikipediaScrapper().fill_episode_name(episode)

    def process_season(self, season: Season):
        super(AnimeProcessor, self).process_season(season)

        finder = MalAPI()
        season.metadata = finder.get_anime_details(anime_id=finder.find_anime(finder.build_search_keyword(season)))

        WikipediaScrapper().fill_season_names(season)

    def process_show(self, show: Show):
        super(AnimeProcessor, self).process_show(show)

        finder = MalAPI()
        show.metadata = finder.get_anime_details(anime_id=finder.find_anime(finder.build_search_keyword(show)))

        WikipediaScrapper().fill_show_names(show)
