from typing import Dict, List

from core.repositories import (
    GoalRepository,
    HabitRepository,
    TaskRepository,
    SkillRepository,
    BoardRepository
)


class MemoryRepository(
    GoalRepository,
    HabitRepository,
    TaskRepository,
    SkillRepository,
    BoardRepository
):
    def __init__(self, data: Dict[int, object]=None):
        if data:
            self.data = data
        else:
            self.data = {}

    def get(self, id: int):
        return self.data.get(id)

    def all(self) -> List:
        return list(self.data.values())

    def create_update(self, object):
        if not object.id:
            if self.data:
                object.id = max(self.data.keys()) + 1
            else:
                object.id = 1
        self.data[object.id] = object
        return object

    def search(self, key):
        return [val for val in self.data.values() if key in val.name]

    def delete(self, id):
        if id not in self.data:
            return
        del self.data[id]

