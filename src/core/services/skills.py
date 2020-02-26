from core.models.skills import Skill
from core.services import Context, ServiceMixin


class SkillService(ServiceMixin[Skill]):

    def __init__(self, context: Context):
        super(SkillService, self).__init__(context, Skill)

    @property
    def repo(self):
        return self.context.skill_repo
