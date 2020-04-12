from typing import List

from core.models.skills import Skill, LevelCounter, LevelRequisite
from core.services import Context, ServiceMixin


class SkillService(ServiceMixin[Skill]):

    def __init__(self, context: Context):
        super(SkillService, self).__init__(context, Skill)

    @property
    def repo(self):
        return self.context.skill_repo

    def level_up(self, skill_level_counter: LevelCounter):
        skill = self.repo.get(skill_level_counter.skill_id)
        skill.update(skill_level_counter)
        return self.repo.create_update(skill)

    def check_requisites(self, requisites: List[LevelRequisite]):
        for requisite in requisites:
            skill = self.get(requisite.skill_id)
            if skill.level.current < requisite.level:
                raise SkillRequisiteNotMetError(skill, requisite)


class SkillRequisiteNotMetError(Exception):
    def __init__(self, skill, req):
        msg = (
            f"Skill requirement not met: {skill.name} "
            f"curr = {skill.level.current} < req = {req.level}"
        )
        super(SkillRequisiteNotMetError, self).__init__(msg)

