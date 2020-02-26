from collections import namedtuple
from dataclasses import dataclass

from core.models import Iternary


Level = namedtuple("Level", ['current', 'max_cap'])


@dataclass
class Skill(Iternary):
    level: Level = Level(1, 10)

    def up(self, level_up: int):
        if self.level.max_cap <= (self.level.current + level_up):
            self.level.current = self.level.max_cap
        self.level = Level(self.level.current + level_up,
                           self.level.max_cap)

    def down(self, level_down: int):
        if 1 >= (self.level.current - level_down):
            self.level.current = 1
        self.level = Level(self.level.current - level_down, self.level.max_cap)

    def __repr__(self):
        return f"([{self.id}] {self.name} {self.level.current/self.level.max_cap})"

    def __hash__(self):
        return hash(self.id)