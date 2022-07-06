import json
import re
from dataclasses import dataclass
from pydoc import locate
from typing import List, Optional, Tuple, Any, Dict

from responses import RequestsMock

from src.core.models import MediaItem
from src.matchers import MediaType


@dataclass
class TestObject:
    item: MediaItem
    media_type: MediaType
    expected_names: List[str]
    fixtures: List[Tuple[str, Optional[str]]]


def configure_test(test_object: TestObject, responses: RequestsMock, mocks: Dict[str, Any]):
    for key, value in test_object.fixtures:
        mock_name, key = key.split(':')
        ttype, parsed_value = __process_fixture(value)
        if mock_name == 're':
            if ttype == 'json':
                responses.add(responses.GET, url=re.compile(key), json=parsed_value)
                continue
            if ttype == 'html':
                responses.add(responses.GET, url=re.compile(key), body=parsed_value)
                continue
            if ttype is None:
                responses.add(responses.GET, url=re.compile(key), status=404)
                continue

        # Configure mock functions
        getattr(mocks[mock_name], key).return_value = parsed_value


def load_page(path: str):
    with open(path, 'r') as f:
        data = f.read()
        f.close()
    return data


def load_json(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
        f.close()
    return data


def __process_fixture(value: Optional[str]):
    if value is None:
        return None, None

    t, v = value.split(':')
    if t == 'json':
        return t, load_json(v)
    if t == 'html':
        return t, load_page(v)

    nt = locate(t)
    return t, nt(v)
