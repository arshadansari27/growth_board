from datetime import datetime

HABIT_TYPE_COUNTER = 'counter'
HABIT_TYPE_BOOLEAN = 'boolean'

@dataclass
class Habit:
    id: int
    name: str
    hotspots: List["Hotspot"]
    description: str
    scheduled_start: datetime
    scheduled_end: datetime
    habit_type: str


@dataclass
class CounterTracking:
    id: int
    habit: Habit
    date: datetime
    value: int


@dataclass
class BooleanTracking:
    id: int
    habit: Habit
    date: datetime
    value: boolean
