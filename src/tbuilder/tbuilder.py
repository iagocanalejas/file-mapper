import os
from abc import ABC
from abc import abstractmethod
from typing import List

from src.core.types import Object
from src.tbuilder.models import Directory
from src.tbuilder.models import File
from src.tbuilder.models import Item


class Tree(ABC, Object):
    _item: Item

    def __new__(cls, *args, path: str, **kwargs):  # pragma: no cover
        if os.path.isfile(path):
            return object.__new__(_SimpleTree)
        return object.__new__(_Tree)

    @property
    def is_file(self) -> bool:
        return isinstance(self._item, File)

    @property
    def is_directory(self) -> bool:
        return isinstance(self._item, Directory)

    @property
    def name(self) -> str:
        return self._item.name

    @property
    def path(self) -> str:
        return self._item.base_path

    @property
    @abstractmethod
    def root(self) -> Item:
        pass

    @property
    @abstractmethod
    def childs(self) -> List[Item]:
        pass


class _SimpleTree(Tree):
    _item: File

    def __init__(self, path: str):
        self._item = File(base_path=os.path.dirname(path), name=os.path.basename(path), parent=None)

    @property
    def root(self) -> File:
        return self._item

    @property
    def childs(self) -> List[Item]:
        return []


class _Tree(Tree):
    _item: Directory

    def __init__(self, path: str):
        self._item = Directory(base_path=os.path.dirname(path), name=os.path.basename(path), parent=None)
        self.__build(self._item)

    @property
    def root(self) -> Directory:
        return self._item

    @property
    def childs(self) -> List[Item]:
        return self._item.childs

    def __build(self, directory: Directory):
        for item in os.listdir(directory.path):
            full_path = os.path.join(directory.path, item)

            if os.path.isfile(full_path):
                directory.childs.append(File(base_path=directory.path, name=item, parent=directory))
                continue

            new_directory = Directory(base_path=directory.path, name=item, parent=directory)
            self.__build(new_directory)
            directory.childs.append(new_directory)
