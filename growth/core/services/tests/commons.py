from typing import TypeVar

import pytest

from ...models.objectives import Goal
from .. import in_memory_context_factory, Context, ServiceMixin


@pytest.fixture
def base_service() -> ServiceMixin[Goal]:
    class U(ServiceMixin[Goal]):
        def __init__(self):
            super(U, self).__init__(in_memory_context_factory(), Goal)
        @property
        def repo(self):
            return self.context.goal_repo

    return U()


T = TypeVar('T')


def test_service_basics(base_service: ServiceMixin[T]):
    goal = base_service.new('name-test-1', 'description-test')
    assert goal.id is not None
    goal2 = base_service.new('name-test-2', 'description-test')
    assert goal2.id is not None
    assert len(base_service.search_by_name('name-test-1')) is 1
    goals = base_service.list()
    assert len(goals) is 2
    assert base_service.get(goal.id).id == goal.id
    goal_1 = base_service.update_name(goal.id, 'new-name-1')
    assert goal.id == goal_1.id
    goal3 = base_service.new('name-test-2', 'description-test')

    base_service.set_before(goal2, goal3)
    base_service.set_after(goal2, goal)
    assert goal3 in goal2.next
    assert goal in goal2.previous
    base_service.remove_from_after(goal2, goal)
    assert goal not in goal2.previous
    base_service.remove_from_before(goal2, goal3)
    assert goal not in goal2.previous






