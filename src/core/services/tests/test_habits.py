import datetime
import random

import pytest

from core.models.objectives import PROGRESS_TYPE_VALUE, Frequency, \
    FREQUENCY_WEEKLY
from core.services import in_memory_context_factory
from core.services.habits import HabitService


@pytest.fixture(scope='module')
def context():
    return in_memory_context_factory()


@pytest.fixture
def habit_service(context):
    return HabitService(context)


def test_habit_date_management(habit_service: HabitService):
    dates = [datetime.datetime(2019, 10, 1) + datetime.timedelta(days=(i))
             for i in range(50)]
    habit = habit_service.new('test-goal', Frequency(FREQUENCY_WEEKLY, 3),
                              PROGRESS_TYPE_VALUE, 'test-desc', )
    removes = []
    for date in dates:
        if random.random()  > 0.3:
            r = int(random.randint(1, 10))
        else:
            r = 0
        habit = habit_service.add_or_update_event(habit.id, date, r)
        removes.append(date)
    habit.update_rating()
    assert habit.rating > 0
    for remove in removes:
        habit = habit_service.remove_event(habit.id, remove)
        habit.update_rating()
    assert habit.rating == 0
