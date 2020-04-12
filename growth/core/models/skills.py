from collections import namedtuple
from dataclasses import dataclass
from typing import Set

from . import Item


Level = namedtuple("Level", ['current', 'max_cap'])
LevelCounter = namedtuple("LevelCounter", ['type', 'skill_id', 'value'])
LevelRequisite = namedtuple("LevelCounter", ['skill_id', 'level'])
LEVEL_UP = 'up'
LEVEL_DOWN = 'down'


@dataclass
class Skill(Item):
    level: Level = Level(1, 10)

    def __init__(self, id: int, name: str, level: Level, description: str = None,
                 next_items: Set["Item"] = None, previous_items: Set["Item"] = None,
                 icon: str = None):
        super(Skill, self).__init__(id, name, description, next_items, previous_items, icon)
        self.level = level

    def update(self, counter: LevelCounter):
        assert self.id == counter.skill_id
        if counter.type == LEVEL_UP:
            self._up(counter.value)
        elif counter.type == LEVEL_DOWN:
            self._down(counter.value)
        else:
            raise NotImplementedError

    @staticmethod
    def create_level_prerequisite(skill: "Skill", required_level: int):
        assert required_level <= skill.level.max_cap
        return LevelRequisite(skill.id, required_level)

    @staticmethod
    def create_level_up_counter(skill: "Skill", count: int):
        return LevelCounter(LEVEL_UP, skill.id, count)

    @staticmethod
    def create_level_down_counter(skill: "Skill", count):
        return LevelCounter(LEVEL_DOWN, skill.id, count)

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

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.level.current == other
        return super(Skill, self).__eq__(other)

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.level.current < other
        return super(Skill, self).__lt__(other)

    def __le__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.level.current <= other
        return super(Skill, self).__le__(other)

    def __gt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.level.current > other
        return super(Skill, self).__gt__(other)

    def __ge__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.level.current >= other
        return super(Skill, self).__ge__(other)
