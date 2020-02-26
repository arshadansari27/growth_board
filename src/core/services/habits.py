from datetime import datetime
from typing import Any

from core.models import Iternary
from core.models.objectives import Habit, PROGRESS_TYPE_BOOLEAN, \
    PROGRESS_TYPE_VALUE
from core.services import Context, ServiceMixin


class HabitService(ServiceMixin[Habit]):

    def __init__(self, context: Context):
        super(HabitService, self).__init__(context, Habit)

    @property
    def repo(self):
        return self.context.habit_repo

    def add_or_update_event(self, habit_id: int, date: datetime, value: Any):
        habit = self.repo.get(habit_id)
        if habit.progress_type == PROGRESS_TYPE_BOOLEAN:
            assert isinstance(value, bool)
        if habit.progress_type == PROGRESS_TYPE_VALUE:
            assert isinstance(value, int) or isinstance(value, float)
        habit.set_date(date, value)
        return self.repo.create_update(habit)

    def remove_event(self, habit_id: int, date: datetime):
        habit = self.repo.get(habit_id)
        habit.unset_date(date)
        return self.repo.create_update(habit)

