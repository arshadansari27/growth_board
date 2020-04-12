import datetime
from typing import Any, List

from core.models.objectives import Goal, Task, Due
from core.models.skills import LevelRequisite, LevelCounter
from core.services import Context, ServiceMixin
from core.services.skills import SkillService


class GoalService(ServiceMixin[Goal]):

    def __init__(self, context: Context):
        super(GoalService, self).__init__(context, Goal)
        self.task_service = TaskService(context)
        self.skill_service = SkillService(context)

    @property
    def repo(self):
        return self.context.goal_repo

    def update_progress(self, goal_id: int, value: Any):
        goal = self.repo.get(goal_id)
        if goal.skill_requisites:
            self.skill_service.check_requisites(goal.skill_requisites)
        goal.update(value)
        if goal.skill_requisites and goal.progress >= 100:
            for reward in goal.skill_rewards:
                self.skill_service.level_up(reward)
        return self.repo.create_update(goal)

    def update_due(
            self,
            goal_id: int,
            end_due: datetime,
            start_due: datetime=None):
        goal = self.repo.get(goal_id)
        due = Due(start_due, end_due)
        goal.due = due
        return self.repo.create_update(goal)

    def new(
            self,
            name,
            description=None,
            progress_type: str=None,
            requisites: List[LevelRequisite]=None,
            rewards: List[LevelCounter] = None,
    ) -> Goal:
        goal = Goal(
                None,
                name=name,
                description=description,
                progress_type=progress_type,
                skill_requisites=requisites,
                skill_rewards=rewards,
        )
        return self.repo.create_update(goal)

    def new_task(self, goal_id: int, name: str, description: str):
        goal = self.repo.get(goal_id)
        task = self.task_service.new(name, description)
        goal.add_task(task)
        return self.repo.create_update(goal)

    def delete_task(self, goal_id: int, task_id: int):
        goal = self.repo.get(goal_id)
        task = self.task_service.get(task_id)
        goal.remove_task(task)
        self.task_service.delete(task)
        return self.repo.create_update(goal)


class TaskService(ServiceMixin[Task]):
    def __init__(self, context: Context):
        super(TaskService, self).__init__(context, Task)

    @property
    def repo(self):
        return self.context.task_repo

    def mark_as_complete(self, task: Task):
        task.progress = 100
        task.completed = True
        return self.repo.create_update(task)

    def mark_as_incomplete(self, task: Task):
        task.progress = 0
        task.completed = False
        return self.repo.create_update(task)