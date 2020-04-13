from datetime import datetime

from growth.core.models.objectives import PROGRESS_TYPE_VALUE
from growth.core.models.objectives.habits import HabitTracker, Habit, FrequencyDaily, FrequencyWeekly, FrequencyMonthly, \
    FrequencyYearly, TARGET_TYPE_MAX, calculate_rating
import pytest


@pytest.fixture
def daily_tracking_mock():
    class MockValue:
        def __init__(self, val):
            self.value = val

        def calculate_value(self):
            return self.value

    return [
        MockValue(1),
        MockValue(1),
        MockValue(1),
        MockValue(0),
        MockValue(0),
        MockValue(0),
    ]

@pytest.fixture
def daily_habit():
    daily_freq = FrequencyDaily(12, 20)
    habit = Habit('1', '1', PROGRESS_TYPE_VALUE, daily_freq,
                  TARGET_TYPE_MAX, 10, True, False)

    HabitTracker('1', habit, datetime(2020, 1, 1), 5),
    HabitTracker('2', habit, datetime(2020, 1, 2), 11),
    HabitTracker('3', habit, datetime(2020, 1, 3), 10),
    HabitTracker('4', habit, datetime(2020, 1, 4), 12)
    return habit


@pytest.fixture
def weekly_habit():
    weekly_freq = FrequencyWeekly(12, 20, tuple([0, 3, 5]))
    habit = Habit('1', '1', PROGRESS_TYPE_VALUE, weekly_freq,
                  TARGET_TYPE_MAX, 10, True, False)

    HabitTracker('1', habit, datetime(2020, 4, 13), 5),
    HabitTracker('2', habit, datetime(2020, 4, 16), 11),
    HabitTracker('3', habit, datetime(2020, 4, 18), 10),
    HabitTracker('4', habit, datetime(2020, 4, 20), 12)
    return habit


def test_calculate_rating(daily_tracking_mock):
    assert calculate_rating(daily_tracking_mock) == 0.5


def test_habit_tracking_habit_daily(daily_habit):
    assert daily_habit.rating == 0.5


def test_habit_tracking_habit_weekly(weekly_habit):
    assert weekly_habit.rating == 0.5

def test_habit_generate_next_tracker_on_daily(daily_habit):
    tracker = daily_habit.generate_next_tracker()
    tracker.date == datetime(2020, 1, 5)


def test_habit_generate_next_tracker_on_weekly(weekly_habit):
    tracker = weekly_habit.generate_next_tracker()
    assert tracker.date == datetime(2020, 4, 23, 0, 0), f"Found date {tracker.date}"
    tracker = weekly_habit.generate_next_tracker()
    assert tracker.date == datetime(2020, 4, 25, 0, 0), f"Found date {tracker.date}"
    tracker = weekly_habit.generate_next_tracker()
    assert tracker.date == datetime(2020, 4, 27, 0, 0), f"Found date {tracker.date}"


def test_habit_generate_next_tracker_on_monthly():

    monthly_freq = FrequencyMonthly(12, 20, 1)
    habit = Habit('1', '1', PROGRESS_TYPE_VALUE, monthly_freq,
                  TARGET_TYPE_MAX, 10, True, False)
    tracker  = habit.generate_next_tracker()
    assert tracker.date == datetime.today().replace(day=monthly_freq.day, hour=0, minute=0, second=0, microsecond=0), f"Found date {tracker.date}"
    tracker  = habit.generate_next_tracker()
    assert tracker.date == datetime.today().replace(month=datetime.today().month + 1, day=monthly_freq.day, hour=0, minute=0, second=0, microsecond=0), f"Found date {tracker.date}"


def test_habit_generate_next_tracker_on_yearly():

    yearly_freq = FrequencyYearly(12, 20, 1, 1)
    habit = Habit('1', '1', PROGRESS_TYPE_VALUE, yearly_freq,
                  TARGET_TYPE_MAX, 10, True, False)
    tracker  = habit.generate_next_tracker()
    assert tracker.date == datetime.today().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0), f"Found date {tracker.date}"
    tracker  = habit.generate_next_tracker()
    assert tracker.date == datetime.today().replace(year=datetime.today().year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0), f"Found date {tracker.date}"


