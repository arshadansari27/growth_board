from datetime import datetime
from typing import Any, List

from core.models.objectives import Habit, PROGRESS_TYPE_BOOLEAN, \
    PROGRESS_TYPE_VALUE, Frequency
from core.models.skills import LevelRequisite
from core.services import Context, ServiceMixin
from core.services.skills import SkillService


class HabitService(ServiceMixin[Habit]):

    def __init__(self, context: Context):
        super(HabitService, self).__init__(context, Habit)
        self.skill_service = SkillService(context)

    @property
    def repo(self):
        return self.context.habit_repo

    def new(
            self,
            name,
            frequency: Frequency,
            progress_type: str,
            requisites: List[LevelRequisite]=None,
            description=None,
    ) -> Habit:
        habit = Habit(
                None,
                name=name,
                frequency=frequency,
                description=description,
                progress_type=progress_type,
                skill_requisites=requisites,
        )
        return self.repo.create_update(habit)

    def update_rating(self, habit_id: int):
        habit = self.repo.get(habit_id)
        if habit.skill_requisites:
            self.skill_service.check_requisites(habit.skill_requisites)
        habit.update_rating()
        return self.repo.create_update(habit)

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

