from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Set, Dict
from uuid import uuid4

from . import PROGRESS_TYPE_BOOLEAN, PROGRESS_TYPE_TASK, PROGRESS_TYPE_VALUE

FREQUENCY_DAILY = 'daily'
FREQUENCY_WEEKLY = 'weekly'
FREQUENCY_MONTHLY = 'monthly'
FREQUENCY_YEARLY = 'yearly'

TARGET_TYPE_MAX = 1
TARGET_TYPE_MIN = -1


class Habit:

    def __init__(self, uuid: int, name: str,
                 progress_type: str,
                 frequency: "Frequency",
                 target_type: int,
                 target_value: int,
                 active: bool,
                 completed: bool = None,
                 priority: int = None,
                 description: str = None,
                 rating: int = None,
                 tracking: Dict[datetime, "HabitTracker"] = None,
                 tags: List[str] = None):
        self.uuid = uuid
        self.name = name
        self.active = active
        self.target_type = target_type
        self.target_value = target_value
        self.completed = completed
        self.priority = priority
        self.description = description
        self.rating = rating
        self.tags = tags
        self.progress_type: str = progress_type
        self.frequency: "Frequency" = frequency
        self.tracking = tracking
        if not self.tracking:
            self.tracking = {}

    def __hash__(self):
        return hash(self.uuid)

    def generate_next_trackers(self, current_date: datetime):
        pass  # TODO: get habit tracking objects by current date and max date


@dataclass(eq=True)
class Frequency:
    start_time_hour: int
    start_time_minute: int


@dataclass
class FrequencyDaily(Frequency):
    type: str = FREQUENCY_DAILY


@dataclass
class FrequencyWeekly(Frequency):
    days: List[int]
    type = FREQUENCY_WEEKLY


@dataclass
class FrequencyMonthly(Frequency):
    day: int
    type: str = FREQUENCY_MONTHLY


@dataclass
class FrequencyYearly(Frequency):
    day: int
    month: int
    type: str = FREQUENCY_YEARLY


class HabitTracker:
    def __init__(self, uuid: str, habit: Habit, date: datetime, value: int):
        self.uuid = uuid
        self.date = date
        self.value = value
        self.habit = habit
        self.habit.tracking.append(self)

    def __hash__(self):
        return hash(self.uuid)

    def calculate_value(self):
        if self.habit.target_type == TARGET_TYPE_MIN:
            return 1 if self.habit.target_value <= self.value else 0
        elif self.habit.target_type == TARGET_TYPE_MAX:
            return 1 if self.habit.target_value >= self.value else 0
        else:
            raise Exception(f"Invalid Target Type {self.habit.target_type}")


def calculate_rating(daily_tracking, from_date, to_date):
    tracked = [u for u in daily_tracking if from_date <= u.date <= to_date]
    return round(float(sum(t.calculate_value() for t in tracked)) / len(tracked), 2)


