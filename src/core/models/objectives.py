from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Set

from core.models import Iternary


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
    progress: int = None
    tasks: Set[Task] = None

    def add_task(self, task: Task):
        if not self.tasks:
            self.tasks = set()
        self.tasks.add(task)

    def remove_task(self, task:Task):
        if not self.tasks or task not in self.tasks:
            return
        self.tasks.remove(task)

    def __repr__(self):
        return f"([{self.id}] {self.name})"

    def __hash__(self):
        return hash(self.id)


@dataclass(eq=True, order=True)
class Habit(Objective):
    done_dates: Dict[datetime, object] = None

    def set_date(self, date: datetime, value: object):
        if not self.done_dates:
            self.done_dates = {}
        self.done_dates[date] = value

    def unset_date(self, date: datetime):
        if not self.done_dates or date not in self.done_dates:
            return
        del self.done_dates[date]

    def __repr__(self):
        return f"([{self.id}] {self.name})"

    def __hash__(self):
        return hash(self.id)