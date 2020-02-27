from dataclasses import dataclass
from queue import Queue
from typing import Set

from core.models import Iternary


@dataclass(eq=True, order=True)
class Board:
    id: int
    name: str=None
    description: str=None
    iternaries: Set[Iternary]=None

    def _setup(self):
        if not self.iternaries:
            self.iternaries = set()

    def add(self, iternary: Iternary):
        self._setup()
        self.iternaries.add(iternary)

    def remove(self, iternary: Iternary):
        self._setup()
        self.iternaries.remove(iternary)

    def iterate(self):
        _list = list()
        queue = Queue()
        for iternary in self.iternaries:
            if not iternary.previous:
                queue.put(iternary)
        while not queue.empty():
            itr = queue.get()
            for i in itr.next:
                queue.put(i)
            _list.append(itr)
        return _list