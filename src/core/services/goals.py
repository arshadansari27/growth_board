from typing import List

from core.models import Board, Iternary
from core.services import Context


class GoalService:
    def __init__(self, context: Context):
        self.context = context
        self.goal_repo = context.goal_repo

    def new(self, name, description=None) -> Board:
        plan_map = Board(None, name=name, description=description)
        plan_map = self.goal_repo.create_update(plan_map)
        return plan_map

    def search_by_name(self, name_like: str) -> List[Board]:
        return self.goal_repo.search(name_like)

    def get(self, id: int) -> Board:
        return self.goal_repo.get(id)

    def list(self) -> List[Board]:
        return self.goal_repo.all()

    def update_name(self, id: int, new_name: str):
        plan_map = self.goal_repo.get(id)
        plan_map.name = new_name
        return self.goal_repo.create_update(plan_map)

    def update_description(self, id: int, new_description: str):
        plan_map = self.goal_repo.get(id)
        plan_map.description = new_description
        return self.goal_repo.create_update(plan_map)

    def add_iternary_to_map(
            self,
            plan_map: Board,
            iternary: Iternary,
            after: Iternary,
            before: Iternary):
        plan_map.add(iternary, after=after, before=before)
        return self.goal_repo.create_update(plan_map)

    def remove_iternary_from_map(self, plan_map: Board, iternary: Iternary):
        plan_map.remove(iternary)
        return self.goal_repo.create_update(plan_map)

