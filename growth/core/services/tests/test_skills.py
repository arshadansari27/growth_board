import pytest

from .. import in_memory_context_factory
from ..skills import SkillService
from ...models.skills import Skill


@pytest.fixture(scope='module')
def context():
    return in_memory_context_factory()


@pytest.fixture
def skill_service(context):
    return SkillService(context)


def test_skill_levelling_up(skill_service: SkillService):
    skill = skill_service.new('skill-test-1', 'skill-description-1')
    level_up_counter = Skill.create_level_up_counter(skill, 5)
    skill = skill_service.level_up(level_up_counter)
    assert skill.level.current == 6
    skill = skill_service.level_up(level_up_counter)
    assert skill.level.current == skill.level.max_cap

