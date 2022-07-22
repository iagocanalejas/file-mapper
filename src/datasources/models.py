from dataclasses import dataclass
from typing import Dict
from typing import Optional

from src.core.types import Language


@dataclass
class APIData:
    id: str
    _title: str
    title_lang: Language
    alternative_titles: Dict[str, str]

    def __str__(self):
        return f'{self.id} -- {self._title}'

    def __init__(self, d: Dict):
        self.id = str(d['id'])

    def title(self, lang: Language = Language.JA) -> Optional[str]:
        if lang != self.title_lang and lang.value in self.alternative_titles and self.alternative_titles[lang.value]:
            return self.alternative_titles[lang.value]
        return self._title


@dataclass
class MalData(APIData):
    title_lang = Language.JA

    def __init__(self, d: Dict):
        super().__init__(d)
        self._title = d['title']
        self.alternative_titles = d['alternative_titles']


@dataclass
class AnilistData(APIData):
    title_lang = Language.JA

    def __init__(self, d: Dict):
        super().__init__(d)
        self._title = d['title']['romaji']
        self.alternative_titles = {'ja': d['title']['romaji'], 'en': d['title']['english']}


@dataclass
class ImdbData(APIData):
    title_lang = Language.EN

    def __init__(self, d: Dict):
        super().__init__(d)
        self._title = d['title']
        self.alternative_titles = {Language.EN.value: d['title']}
