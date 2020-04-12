from dataclasses import dataclass
from datetime import datetime
from typing import List, Set

from .. import Item

PROGRESS_TYPE_TASK = 'tasks'
PROGRESS_TYPE_VALUE = 'value'
PROGRESS_TYPE_BOOLEAN = 'boolean'


@dataclass(eq=True, order=True)
class Due:
    start: datetime
    end: datetime


@dataclass(eq=True, order=True)
class Objective(Item):
    due: Due = None
    completed: bool = None
    priority: int = None
    tags: List[str] = None

    def __init__(self, id: int, name: str, due: Due = None,
                 completed: bool = None, priority: int = None,
                 description: str = None,
                 next_items: Set["Item"] = None, previous_items: Set["Item"] = None,
                 tags: List[str] = None, icon: str = None):
        super(Objective, self).__init__(id, name, description, next_items, previous_items, icon)
        self.due = due
        self.completed = completed
        self.priority = priority
        self.tags = tags


from .goals import Goal
from .tasks import Task
from .habits import Habit, Frequency, FREQUENCY_DAILY, FREQUENCY_MONTHLY, FREQUENCY_WEEKLY

__all__ = [Goal, Task, Task, Frequency, FREQUENCY_DAILY, FREQUENCY_MONTHLY, FREQUENCY_WEEKLY]
