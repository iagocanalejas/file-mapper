import re
from collections.abc import Iterable
from enum import Enum
from typing import Callable
from typing import List
from typing import Optional


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


def whitespaces_clean(word: str) -> str:
    return re.sub(r' +', ' ', word).strip()


def generic_clean(word: str) -> str:
    word = word.replace('_', ' ')
    word = word.replace(' (1)', '')  # remove ' (1)' for copied files
    word = word.replace(' (TV)', '')  # remove ' (TV)' for some season names
    return whitespaces_clean(word)


def remove_tracker(word: str) -> str:
    return re.sub(r'\[[\w\d\-_−–#: !+]*]', '', word).strip()


def remove_parenthesis(word: str) -> str:
    return re.sub(r'\([\w\d\-_−–#: !+]*\)', '', word).strip()


def remove_brackets(word: str) -> str:
    return re.sub(r'\{[\w\d\-_−–#: !+]*}', '', word).strip()


def remove_episode(word: str) -> str:
    match = re.search(r'( - )?e(pisode )?\d+| - \d+', word, re.IGNORECASE)
    return word.replace(match.group(0), '').strip() if match is not None else word


def remove_episode_name(word: str) -> str:
    match = re.search(r'\d+([\s-]+[\w\s]*)', word, re.IGNORECASE)
    return word.split(match.group(1))[0].strip() if match is not None else word


def remove_season(word: str) -> str:
    match = re.search(r's(eason )?\d+', word, re.IGNORECASE)
    return word.replace(match.group(0), '').strip() if match is not None else word


def remove_extension(word: str) -> str:
    return re.sub(r'\.[\w\d]{3,4}', '', word).strip()


def remove_trailing_hyphen(word: str) -> str:
    return re.sub(r'- ?$', '', word).strip()


def retrieve_extension(word: str) -> Optional[str]:
    match = re.search(r'\.[\w\d]{3,4}$', word, re.IGNORECASE)
    if match is not None:
        return match.group(0)[1:]


def clean_output(out: str) -> str:
    out = out.replace('<', '') \
        .replace('>', '') \
        .replace(':', ' -') \
        .replace(';', '') \
        .replace('"', '') \
        .replace('\\', '-') \
        .replace('/', '-') \
        .replace('|', '') \
        .replace('?', '') \
        .replace('*', '')
    return whitespaces_clean(out)


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


def closest_result(keyword: str, elements: List[str]) -> str:
    best_distance = levenshtein_distance(keyword, elements[0])
    best_word = elements[0]
    for w in elements:
        d = levenshtein_distance(keyword, w)
        if d < best_distance:
            best_distance = d
            best_word = w

    return best_word


def apply(functions: Iterable[Callable[[str], str]], arg: Iterable[str] | str):
    if type(arg) == str:
        for f in functions:
            arg = f(arg)
        return arg
    if isinstance(arg, Iterable):
        return [apply(functions, a) for a in arg]
    return arg


# decorator
def apply_clean(clean_functions: Iterable[Callable[[str], str]]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            args = [apply(clean_functions, arg) for arg in args]
            kwargs = {key: apply(clean_functions, value) for key, value in kwargs.items()}
            return func(*args, **kwargs)

        return wrapper

    return decorator


def accepts(*types):
    def check_accepts(f):
        def new_f(*args, **kwds):
            for (a, t) in zip(args[1:], types):
                assert isinstance(a, t), \
                    f'arg {a!r} does not match {t}'
            return f(*args, **kwds)

        new_f.__name__ = f.__name__
        return new_f

    return check_accepts
