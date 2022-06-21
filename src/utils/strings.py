import re
from collections.abc import Iterable
from enum import Enum
from typing import Callable


class RomanNumbers(Enum):
    I = 1  # noqa
    II = 2
    III = 3
    IV = 4
    V = 5
    VI = 6
    VII = 7
    VIII = 8
    XI = 9


def generic_clean(word: str) -> str:
    word = word.replace('_', ' ')
    word = word.replace(' (1)', '')  # remove ' (1)' for copied files
    return re.sub(r' +', ' ', word).strip()


def remove_tracker(word: str) -> str:
    return re.sub(r'\[[\w\d\-_ +]*]', '', word).strip()


def remove_parenthesis(word: str) -> str:
    return re.sub(r'\([\w\d\-_ +]*\)', '', word).strip()


def remove_extension(word: str) -> str:
    parts = word.split('.')
    if len(parts) == 1:
        return parts[0].strip()
    return ' '.join(word.split('.')[:-1]).strip()


def levenshtein_distance(s1, s2):
    # This function has already been implemented for you.
    # Source of the implementation:
    # https://stackoverflow.com/questions/2460177/edit-distance-in-python
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1],
                                           distances_[-1])))
        distances = distances_
    return distances[-1]


def __apply(functions: Iterable[Callable[[str], str]], arg: Iterable[str] | str):
    if type(arg) == str:
        for f in functions:
            arg = f(arg)
        return arg
    if isinstance(arg, Iterable):
        return [__apply(functions, a) for a in arg]
    return arg


# decorator
def apply_clean(clean_functions: Iterable[Callable[[str], str]]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            args = [__apply(clean_functions, arg) for arg in args]
            kwargs = {key: __apply(clean_functions, value) for key, value in kwargs.items()}
            return func(*args, **kwargs)

        return wrapper

    return decorator
