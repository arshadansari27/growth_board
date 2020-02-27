from dataclasses import dataclass
from typing import Set


class AlreadyDoneError(Exception):
    def __init__(self, f):
        super(AlreadyDoneError, self).__init__(f"Already done {f}")


@dataclass(eq=True, order=True)
class Iternary:
    id: int
    name: str=None
    description: str=None
    next: Set["Iternary"]=None
    previous: Set["Iternary"]=None
    icon: str=None

    def _setup(self, other: "Iternary"=None):
        if not self.next:
            self.next = set()
        if not self.previous:
            self.previous = set()
        if other:
            other._setup()

    def add_next(self, next_iternary: "Iternary"):
        self._setup(next_iternary)
        self.next.add(next_iternary)
        next_iternary.previous.add(self)

    def add_previous(self, previous_iternary: "Iternary"):
        self._setup(previous_iternary)
        self.previous.add(previous_iternary)
        previous_iternary.next.add(self)

    def remove_next(self, next_iternary: "Iternary"):
        if next_iternary in self.next:
            self.next.remove(next_iternary)
        if self in next_iternary.previous:
            next_iternary.previous.remove(self)

    def remove_previous(self, previous_iternary: "Iternary"):
        if previous_iternary in self.previous:
            self.previous.remove(previous_iternary)
        if self in previous_iternary.next:
            previous_iternary.next.remove(self)


