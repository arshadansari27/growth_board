from collections import namedtuple
from dataclasses import dataclass

from core.models import Iternary


Level = namedtuple("Level", ['current', 'max_cap'])
LevelCounter = namedtuple("LevelCounter", ['type', 'skill_id', 'value'])
LEVEL_UP = 'up'
LEVEL_DOWN = 'down'


@dataclass
class Skill(Iternary):
    level: Level = Level(1, 10)

    def update(self, counter: LevelCounter):
        assert self.id == counter.skill_id
        if counter.type == LEVEL_UP:
            self._up(counter.value)
        elif counter.type == LEVEL_DOWN:
            self._down(counter.value)
        else:
            raise NotImplementedError

    @staticmethod
    def create_level_up_counter(skill_id: int, count: int):
        return LevelCounter(LEVEL_UP, skill_id, count)

    @staticmethod
    def create_level_down_counter(skill_id, count):
        return LevelCounter(LEVEL_DOWN, skill_id, count)

    def _up(self, level_up: int):
        if self.level.max_cap <= (self.level.current + level_up):
            self.level = Level(self.level.max_cap, self.level.max_cap)
        else:
            self.level = Level(self.level.current + level_up,
                           self.level.max_cap)

    def _down(self, level_down: int):
        if 1 >= (self.level.current - level_down):
            self.level.current = 1
            self.level = Level(1, self.level.max_cap)
        else:
            self.level = Level(self.level.current - level_down, self.level.max_cap)

    def __repr__(self):
        return f"([{self.id}] {self.name} {self.level.current/self.level.max_cap})"

    def __hash__(self):
        return hash(self.id)