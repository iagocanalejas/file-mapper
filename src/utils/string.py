import re
from collections.abc import Iterable
from enum import Enum
from typing import Callable


class RomanNumbers(Enum):
    I = 1
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


def __clean_arg(arg: Iterable[str] | str):
    if type(arg) == str:
        return generic_clean(arg)
    if isinstance(arg, Iterable):
        return [__clean_arg(a) for a in arg]
    return arg


# decorator
def clean_strings(func):
    def wrapper(*args, **kwargs):
        args = [__clean_arg(arg) for arg in args]
        kwargs = {key: __clean_arg(value) for key, value in kwargs.items()}
        return func(*args, **kwargs)

    return wrapper


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
