from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Set, Any, Union

from . import Iternary
from .skills import LevelRequisite, LevelCounter

PROGRESS_TYPE_TASK = 'tasks'
PROGRESS_TYPE_VALUE = 'value'
PROGRESS_TYPE_BOOLEAN = 'boolean'


@dataclass(eq=True, order=True)
class Due:
    start: datetime
    end: datetime


@dataclass(eq=True, order=True)
class Objective(Iternary):
    due: Due = None
    completed: bool = None
    priority: int = None
    tags: List[str] = None


@dataclass(eq=True, order=True)
class Task(Objective):
    progress: int = None

    def __repr__(self):
        return f"([{self.id}] {self.name})"

    def __hash__(self):
        return hash(self.id)


@dataclass(eq=True, order=True)
class Goal(Objective):
    tasks: Set[Task] = None
    progress: int = None
    progress_type: str = None
    skill_requisites: List[LevelRequisite] = None
    skill_rewards: List[LevelCounter] = None

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


FREQUENCY_DAILY = 'daily'
FREQUENCY_WEEKLY = 'weekly'
FREQUENCY_MONTHLY = 'montly'


@dataclass(eq=True)
class Frequency:
    type: str
    max_count: int = 1


@dataclass(eq=True, order=True)
class Habit(Objective):
    done_dates: Dict[datetime, Union[bool, int]] = None
    progress_type: str = None
    rating: int = None
    frequency: Frequency = None
    skill_requisites: List[LevelRequisite] = None
    skill_rewards: List[LevelCounter] = None

    def __post_init__(self):
        if not self.progress_type:
            self.progress_type = PROGRESS_TYPE_BOOLEAN

    def set_date(self, date: datetime, value: Union[bool, int]):
        if not self.done_dates:
            self.done_dates = {}
        self.done_dates[date] = value

    def unset_date(self, date: datetime):
        if not self.done_dates or date not in self.done_dates:
            return
        del self.done_dates[date]

    def update_rating(self):
        from .specs import count_progress
        self.rating = 0
        if not self.done_dates:
            return
        self.rating = count_progress(
                self.done_dates, self.progress_type, self.frequency)

    def __repr__(self):
        return f"([{self.id}] {self.name})"

    def __hash__(self):
        return hash(self.id)

