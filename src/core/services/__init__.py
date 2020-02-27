import abc
from typing import TypeVar, Generic, List, Any, Union

from core.models import Board
from core.models.objectives import Goal, Habit, Task
from core.models.skills import Skill
from core.repositories import BoardRepository, GoalRepository, TaskRepository, \
    HabitRepository, SkillRepository


class Context:
    def __init__(self,
                 board_repo: BoardRepository,
                 goal_repository: GoalRepository,
                 task_repository: TaskRepository,
                 habit_repository: HabitRepository,
                 skill_repository: SkillRepository):
        self.board_repo = board_repo
        self.goal_repo = goal_repository
        self.task_repo = task_repository
        self.habit_repo = habit_repository
        self.skill_repo = skill_repository

    def repository_factory(self, entity: Any):
        if isinstance(entity, Goal):
            return self.goal_repo
        elif isinstance(entity, Habit):
            return self.habit_repo
        elif isinstance(entity, Task):
            return self.task_repo
        elif isinstance(entity, Skill):
            return self.skill_repo
        elif isinstance(entity, Board):
            return self.board_repo
        else:
            raise NotImplementedError


T = TypeVar('T')

All_Types =  Union[Habit, Goal, Task, Skill, Board]


class ServiceMixin(Generic[T], metaclass=abc.ABCMeta):
    def __init__(self, context: Context, Klass: type):
        self.context = context
        self.klass = Klass

    @property
    @abc.abstractmethod
    def repo(self):
        pass

    def new(self, name, description=None) -> T:
        entity = self.klass(None, name=name, description=description)
        return self.repo.create_update(entity)

    def search_by_name(self, name_like: str) -> List[T]:
        return self.repo.search(name_like)

    def get(self, id: int) -> T:
        return self.repo.get(id)

    def delete(self, entity: T):
        for prev in entity.previous:
            prev.remove_next(entity)
        for next in entity.next:
            next.remove_previous(entity)
        self.repo.delete(entity.id)

    def list(self) -> List[T]:
        return self.repo.all()

    def update_name(self, id: int, new_name: str):
        entity = self.repo.get(id)
        entity.name = new_name
        return self.repo.create_update(entity)

    def update_description(self, id: int, new_description: str):
        entity = self.repo.get(id)
        entity.description = new_description
        return self.repo.create_update(entity)

    def set_after(self, entity: All_Types, after: All_Types):
        entity.add_previous(after)
        after_repo = self.context.repository_factory(after)
        after_repo.create_update(after)
        return self.repo.create_update(entity)

    def set_before(self, entity: All_Types, before: All_Types):
        entity.add_next(before)
        before_repo = self.context.repository_factory(before)
        before_repo.create_update(before)
        return self.repo.create_update(entity)

    def remove_from_after(self, entity: All_Types, after: All_Types):
        entity.remove_previous(after)
        after_repo = self.context.repository_factory(after)
        after_repo.create_update(after)
        return self.repo.create_update(entity)

    def remove_from_before(self, entity: All_Types, before: All_Types):
        entity.remove_next(before)
        before_repo = self.context.repository_factory(before)
        before_repo.create_update(before)
        return self.repo.create_update(entity)


def in_memory_context_factory():
    from core.repositories.impl.memory import MemoryRepository
    return Context(MemoryRepository(), MemoryRepository(),
            MemoryRepository(), MemoryRepository(), MemoryRepository())