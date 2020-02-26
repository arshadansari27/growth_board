from core.models.objectives import Goal, Task
from core.services import Context, ServiceMixin


class GoalService(ServiceMixin[Goal]):

    def __init__(self, context: Context):
        super(GoalService, self).__init__(context, Goal)

    @property
    def repo(self):
        return self.context.goal_repo

    def add_task(self, goal: Goal, task: Task):
        goal.add_task(task)
        return self.repo.create_update(goal)

    def remove_task(self, goal: Goal, task: Task):
        goal.remove_task(task)
        return self.repo.create_update(goal)

