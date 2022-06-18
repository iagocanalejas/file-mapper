from abc import ABC, abstractmethod


class Datasource(ABC):
    @property
    def _class_name(self):
        return self.__class__.__name__

    @staticmethod
    @abstractmethod
    def build_search_keyword(item) -> str:
        pass


class API(Datasource, ABC):
    pass


class Scrapper(Datasource, ABC):
    pass
