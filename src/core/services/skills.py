from core.models.skills import Skill, LevelCounter
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
