from dataclasses import dataclass
from queue import Queue
from typing import Set, List, Tuple, Dict

from . import Iternary

STATUS_BACKLOG = 'backlog'
STATUS_READY = 'ready'
STATUS_IN_PROGRESS = 'in-progress'
STATUS_DONE = 'done'


@dataclass(eq=True, order=True)
class Board:
    id: int
    name: str=None
    description: str=None
    iternaries: Set[Iternary]=None
    status_per_iternaries: Dict[str, List[Iternary]] = None
    statuses: Tuple = None

    def __post_init__(self):
        if not self.statuses:
            self.statuses = (
                STATUS_BACKLOG, STATUS_READY, STATUS_IN_PROGRESS, STATUS_DONE
            )

    def _setup(self):
        if not self.iternaries:
            self.iternaries = set()
        if not self.status_per_iternaries:
            self.status_per_iternaries = {}

    def add(self, iternary: Iternary):
        self._setup()
        if iternary in self.iternaries:
            print('Already added')
            return
        self.iternaries.add(iternary)
        self.status_per_iternaries[iternary.id] = self.statuses[0]

    def remove(self, iternary: Iternary):
        self._setup()
        self.iternaries.remove(iternary)
        del self.status_per_iternaries[iternary.id]

    def iterate(self):
        _list = list()
        queue = Queue()
        for iternary in self.iternaries:
            if not iternary.previous:
                queue.put(iternary)
        while not queue.empty():
            itr = queue.get()
            if itr.next:
                for i in itr.next:
                    queue.put(i)
            _list.append(itr)
        return _list

    def status_incr(self, iternary: Iternary):
        assert iternary in self.iternaries
        iternary_status = self.status_per_iternaries[iternary.id]
        if iternary_status == STATUS_DONE:
            raise InvalidStatusError("Status is already done")
        curr_status_index = self.statuses.index(iternary_status)
        if iternary.previous:
            for prev in iternary.previous:
                st = self.status_per_iternaries[prev.id]
                if st != STATUS_DONE and self.statuses.index(st) <= (
                curr_status_index + 1):
                    raise InvalidStatusError("Predecessor iternary still is "
                                             "not in advanced state")
        if iternary.next:
            for next in iternary.next:
                self.status_incr(next)

    def status_decr(self, iternary: Iternary):
        assert iternary in self.iternaries
        iternary_status = self.status_per_iternaries[iternary.id]
        curr_status_index = self.statuses.index(iternary_status)
        if curr_status_index == STATUS_BACKLOG:
            raise InvalidStatusError("Status is already at backlog")
        prev_status = self.statuses[curr_status_index - 1]
        if iternary.next:
            for next in iternary.next:
                st = self.status_per_iternaries[next.id]
                if st != STATUS_BACKLOG and self.statuses.index(st) >= (
                    curr_status_index - 1
                ):
                    raise InvalidStatusError("Successor iternary not in "
                                             "further backwards state")


class InvalidStatusError(Exception):
    def __init__(self, msg):
        super(InvalidStatusError, self).__init__(f'Status Invalid Error: {msg}')


class IncrCommand:
    pass


class DecrCommand:
    pass


class BoardStateStructure:

    def __init__(self):
        self.statuses = (
            STATUS_BACKLOG, STATUS_READY, STATUS_IN_PROGRESS, STATUS_DONE
        )
