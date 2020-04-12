import pytest

from ...models.objectives import Goal
from ..impl.memory import MemoryRepository


@pytest.fixture
def repository():
    return MemoryRepository({})


def test_repo(repository):
    goal = Goal(1)
    goal.name = "test"
    repository.create_update(goal)
    goal = repository.get(1)
    assert goal.name == "test"
