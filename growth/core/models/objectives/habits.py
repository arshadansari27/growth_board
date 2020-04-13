from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Set, Dict, Tuple
from uuid import uuid4

from . import PROGRESS_TYPE_BOOLEAN, PROGRESS_TYPE_TASK, PROGRESS_TYPE_VALUE

FREQUENCY_DAILY = 'daily'
FREQUENCY_WEEKLY = 'weekly'
FREQUENCY_MONTHLY = 'monthly'
FREQUENCY_YEARLY = 'yearly'

TARGET_TYPE_MAX = 1
TARGET_TYPE_MIN = -1


def create_habit(name, progress_type, target_type, frequency_type, time_hour=None, time_minute=None, days=None, month=None):
    assert progress_type in {PROGRESS_TYPE_BOOLEAN, PROGRESS_TYPE_TASK, PROGRESS_TYPE_VALUE}
    assert target_type in {TARGET_TYPE_MAX, TARGET_TYPE_MAX}
    assert frequency_type in {FREQUENCY_DAILY, FREQUENCY_WEEKLY, FREQUENCY_MONTHLY, FREQUENCY_YEARLY}
    if not time_hour and not time_minute:
        time_hour = 0
        time_minute = 0

    if frequency_type == FREQUENCY_DAILY:
        frequency = FrequencyDaily(time_hour, time_minute)
    elif frequency_type == FREQUENCY_WEEKLY:
        assert isinstance(days, tuple)
        frequency = FrequencyWeekly(time_hour, time_minute, days=days)
    elif frequency_type == FREQUENCY_MONTHLY:
        assert isinstance(days, int)
        frequency = FrequencyMonthly(time_hour, time_minute, days)
    else:
        assert isinstance(days, int)
        assert isinstance(month, int)
        frequency = FrequencyYearly(time_hour, time_minute, days, month)
    return Habit(uuid4(), name, progress_type, frequency, target_type)


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
        self.tags = tags
        self.progress_type: str = progress_type
        self.frequency: "Frequency" = frequency
        self.tracking = tracking
        if not self.tracking:
            self.tracking = {}

    @property
    def rating(self):
        return calculate_rating(self.tracking.values())

    def generate_next_tracker(self):
        if isinstance(self.frequency, FrequencyDaily):
            if self.tracking:
                date = max(self.tracking) + timedelta(days=1)
            else:
                date = datetime.today()
        elif isinstance(self.frequency, FrequencyWeekly):
            #TODO: Simplify the following logic with use from calendar
            days = sorted(self.frequency.days)
            if not self.tracking:
                current_date = datetime.today()
            else:
                current_date = max(self.tracking)
            current_week_day = current_date.weekday()
            remain_days_this_week = [u for u in days if u > current_week_day]
            if remain_days_this_week:
                # More days to follow from same week then diff to the next date
                day = remain_days_this_week[0]
                diff = day - current_week_day
            else:
                # Days to follow from next week then diff to the next date by adding values from next week
                # as well as 1 for 0 value of monday
                day = days[0]
                diff = (6 - current_week_day) + day + 1
            date = current_date + timedelta(days=diff)
        elif isinstance(self.frequency, FrequencyMonthly):
            if self.tracking:
                last_date =  max(self.tracking)
                date = (last_date + timedelta(days=30)).replace(day=self.frequency.day)
            else:
                date = datetime.today().replace(day=self.frequency.day, hour=0, minute=0, second=0, microsecond=0)
        elif isinstance(self.frequency, FrequencyYearly):
            if self.tracking:
                last_date =  max(self.tracking)
                date = last_date.replace(year=last_date.year + 1)
            else:
                date = datetime.today().replace(month=self.frequency.month, day=self.frequency.day, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise NotImplementedError
        return HabitTracker(uuid4(), self, date, 0)

    def __hash__(self):
        return hash(self.uuid)

@dataclass(eq=True)
class Frequency:
    time_hour: int
    time_minute: int


@dataclass
class FrequencyDaily(Frequency):
    type: str = FREQUENCY_DAILY


@dataclass
class FrequencyWeekly(Frequency):
    days: Tuple = (6,)
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
        self.habit.tracking[date] = self

    def __hash__(self):
        return hash(self.uuid)

    def calculate_value(self):
        if self.habit.target_type == TARGET_TYPE_MIN:
            value = 1 if self.habit.target_value <= self.value else 0
        elif self.habit.target_type == TARGET_TYPE_MAX:
            value = 1 if self.habit.target_value >= self.value else 0
        else:
            raise Exception(f"Invalid Target Type {self.habit.target_type}")
        return value


def calculate_rating(daily_tracking):
    return round(float(sum(t.calculate_value() for t in daily_tracking)) / len(daily_tracking), 2)


