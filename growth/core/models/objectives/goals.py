from dataclasses import dataclass
from typing import List, Set

from . import Objective, PROGRESS_TYPE_BOOLEAN, PROGRESS_TYPE_TASK, PROGRESS_TYPE_VALUE, Due
from .tasks import Task
from ..skills import LevelRequisite, LevelCounter


@dataclass(eq=True, order=True)
class Goal(Objective):
    tasks: Set[Task] = None
    progress: int = None
    progress_type: str = None
    skill_requisites: List[LevelRequisite] = None
    skill_rewards: List[LevelCounter] = None

    def __init__(self, id: int, name: str, due: Due = None,
                 tasks: Set[Task] = None, progress: int = None, progress_type: str = None,
                 skill_requisites: List[LevelRequisite] = None, skill_rewards: List[LevelCounter] = None,
                 completed: bool = None, priority: int = None, description: str = None,
                 next_items: Set["Item"] = None, previous_items: Set["Item"] = None,
                 tags: List[str] = None, icon: str = None):
        super(Goal, self).__init__(id, name, due, completed, priority, description, next_items, previous_items, tags, icon)
        self.tasks = tasks
        self.progress = progress
        self.progress_type = progress_type
        self.skill_requisites = skill_requisites
        self.skill_rewards = skill_rewards

    def __post_init__(self):
        if not self.progress_type:
            self.progress_type = PROGRESS_TYPE_BOOLEAN

    def add_task(self, task: Task):
        if not self.tasks:
            self.tasks = set()
        self.tasks.add(task)

    def remove_task(self, task:Task):
        if not self.tasks or task not in self.tasks:
            return
        self.tasks.remove(task)

    def update(self, value):
        def update_value():
            if (self.progress + value) >= 100:
                self.progress = 100
            else:
                self.progress += value

        def update_boolean():
            if value:
                self.progress = 100
            else:
                self.progress = 0

        def update_task():
            value = sum([1 if t.progress == 100 else 0 for t in self.tasks])
            count = len(self.tasks)
            self.progress = int((float(value) / count) * 100)

        if self.progress_type == PROGRESS_TYPE_BOOLEAN:
            update_boolean()
        elif self.progress_type == PROGRESS_TYPE_TASK:
            update_task()
        elif self.progress_type == PROGRESS_TYPE_VALUE:
            update_value()
        else:
            raise NotImplementedError

    def __repr__(self):
        return f"([{self.id}] {self.name})"

    def __hash__(self):
        return hash(self.id)

