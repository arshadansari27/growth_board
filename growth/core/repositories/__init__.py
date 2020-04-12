import abc
from typing import List

from ..models.board import Board
from ..models.objectives import (
    Goal,
    Task,
    Habit,
)
from ..models.skills import Skill


def get_abstract_repository(Klass):
    class _Repository(metaclass=abc.ABCMeta):
        @abc.abstractmethod
        def get(self, id: int) -> Klass:
            pass

        @abc.abstractmethod
        def all(self) -> List[Klass]:
            pass

        @abc.abstractmethod
        def create_update(self, entity: Klass):
            pass

        @abc.abstractmethod
        def search(self, key: str) -> List[Klass]:
            pass

        @abc.abstractmethod
        def delete(self, id: int):
            pass

    return _Repository


class GoalRepository(get_abstract_repository(Goal)):
    pass


class TaskRepository(get_abstract_repository(Task)):
    pass


class HabitRepository(get_abstract_repository(Habit)):
    pass


class SkillRepository(get_abstract_repository(Skill)):
    pass


class BoardRepository(get_abstract_repository(Board)):
    pass
