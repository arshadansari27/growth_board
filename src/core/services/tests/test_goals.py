import datetime

import pytest

from core.models.objectives import PROGRESS_TYPE_TASK, PROGRESS_TYPE_BOOLEAN
from core.models.skills import Skill
from core.services import in_memory_context_factory
from core.services.goals import GoalService, TaskService
from core.services.skills import SkillRequisiteNotMetError


@pytest.fixture(scope='module')
def context():
    return in_memory_context_factory()


@pytest.fixture
def goal_service(context):
    return GoalService(context)


@pytest.fixture
def task_service(context):
    return TaskService(context)


def test_goal_and_skill_requisites(goal_service):
    skill_service = goal_service.skill_service
    skill_1 = skill_service.new('skill-test-1', 'skill-desc')
    skill_2 = skill_service.new('skill-test-2', 'skill-desc')
    req_1 = Skill.create_level_prerequisite(skill_1, 5)
    req_2 = Skill.create_level_prerequisite(skill_2, 5)
    goal = goal_service.new(
            'test-goal',
            'test-desc',
            PROGRESS_TYPE_BOOLEAN,
            requisites=[req_1, req_2])
    try:
        goal_service.update_progress(goal.id, 10)
        raise Exception("Shouldn't update")
    except SkillRequisiteNotMetError:
        pass
    skill_1.update(Skill.create_level_up_counter(skill_1, 5))
    skill_2.update(Skill.create_level_up_counter(skill_2, 5))
    goal_service.update_progress(goal.id, 10)


def test_goal_and_tasks(goal_service, task_service):
    goal = goal_service.new('test-goal', 'test-desc', PROGRESS_TYPE_TASK)
    goal = goal_service.update_due(goal.id, datetime.datetime.now())
    assert goal.due is not None
    goal = goal_service.new_task(goal.id, 'test-task', 'test-task-desc')
    task = list(goal.tasks)[0]
    goal = goal_service.update_progress(goal.id, None)
    assert goal.progress == 0
    task = task_service.mark_as_complete(task)
    assert task.completed
    goal = goal_service.update_progress(goal.id, None)
    assert goal.progress == 100
    task = task_service.mark_as_incomplete(task)
    goal = goal_service.update_progress(goal.id, None)
    assert goal.progress == 0
    assert not task.completed

