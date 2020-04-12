import pytest

from growth.core.models.objectives import Frequency, PROGRESS_TYPE_BOOLEAN, \
    FREQUENCY_DAILY
from growth.core.services import in_memory_context_factory
from growth.core.services.boards import BoardService
from growth.core.services.goals import GoalService
from growth.core.services.habits import HabitService


@pytest.fixture(scope='module')
def context():
    return in_memory_context_factory()


@pytest.fixture
def board_service(context):
    return BoardService(context)


@pytest.fixture
def goal_service(context):
    return GoalService(context)


@pytest.fixture
def habit_service(context):
    return HabitService(context)


def test_iternary_addition_and_removal(board_service, goal_service,
                                       habit_service):
    goal = goal_service.new('name-goal-1', 'description-test')
    habit = habit_service.new('name-habit-2', Frequency(FREQUENCY_DAILY, 1),
                              PROGRESS_TYPE_BOOLEAN, 'description-test')
    goal2 = goal_service.new('name-goal-2', 'description-test')

    goal_service.set_before(habit, goal2)
    goal_service.set_after(habit, goal)
    board = board_service.new('test-name', 'test-description')
    board_service.add_iternary(board.id, goal)
    board_service.add_iternary(board.id, habit)
    board_service.add_iternary(board.id, goal2)
    plan = board_service.list_sorted(board.id)
    assert goal in plan
    assert goal2 in plan
    assert habit in plan

