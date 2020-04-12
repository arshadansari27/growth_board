import datetime
import random

import pytest

from core.models.objectives import PROGRESS_TYPE_VALUE, Frequency, \
    FREQUENCY_WEEKLY, PROGRESS_TYPE_BOOLEAN
from core.models.skills import Skill
from core.services import in_memory_context_factory
from core.services.habits import HabitService
from core.services.skills import SkillRequisiteNotMetError


@pytest.fixture(scope='module')
def context():
    return in_memory_context_factory()


@pytest.fixture
def habit_service(context):
    return HabitService(context)


def test_habit_and_skill_requisites(habit_service):
    skill_service = habit_service.skill_service
    skill_1 = skill_service.new('skill-test-1', 'skill-desc')
    skill_2 = skill_service.new('skill-test-2', 'skill-desc')
    req_1 = Skill.create_level_prerequisite(skill_1, 5)
    req_2 = Skill.create_level_prerequisite(skill_2, 5)
    skill_3 = skill_service.new('skill-test-3', 'skill-desc')
    rew = Skill.create_level_up_counter(skill_3, 5)
    habit = habit_service.new(
            name='test-habit',
            description='test-desc',
            progress_type=PROGRESS_TYPE_BOOLEAN,
            frequency=Frequency(FREQUENCY_WEEKLY, 1),
            requisites=[req_1, req_2],
            rewards=[rew])
    s = skill_service.get(habit.skill_rewards[0].skill_id)
    assert s < 5
    habit = habit_service.add_or_update_event(
            habit.id, datetime.datetime.now(), True)
    try:
        habit_service.update_rating(habit.id)
        raise Exception("Shouldn't update")
    except SkillRequisiteNotMetError:
        pass
    skill_1.update(Skill.create_level_up_counter(skill_1, 5))
    skill_2.update(Skill.create_level_up_counter(skill_2, 5))
    habit = habit_service.update_rating(habit.id)
    s = skill_service.get(habit.skill_rewards[0].skill_id)
    assert s >= 5


def test_habit_date_management(habit_service: HabitService):
    dates = [datetime.datetime(2019, 10, 1) + datetime.timedelta(days=(i))
             for i in range(50)]
    habit = habit_service.new('test-habit', Frequency(FREQUENCY_WEEKLY, 3),
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
