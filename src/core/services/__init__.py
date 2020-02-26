import abc
from typing import T, TypeVar, Generic, List

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


T = TypeVar('T')


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
        print(entity, type(entity))
        entity = self.repo.create_update(entity)
        return entity

    def search_by_name(self, name_like: str) -> List[T]:
        return self.repo.search(name_like)

    def get(self, id: int) -> T:
        return self.repo.get(id)

    def list(self) -> List[T]:
        return self.repo.all()

    def update_name(self, id: int, new_name: str):
        board = self.repo.get(id)
        board.name = new_name
        return self.repo.create_update(board)

    def update_description(self, id: int, new_description: str):
        board = self.repo.get(id)
        board.description = new_description
        return self.repo.create_update(board)


def in_memory_context_factory():
    from core.repositories.impl.memory import MemoryRepository
    return Context(MemoryRepository(), MemoryRepository(),
            MemoryRepository(), MemoryRepository(), MemoryRepository())