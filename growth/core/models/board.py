from dataclasses import dataclass
from queue import Queue
from typing import Set, List, Tuple, Dict

from . import Item

STATUS_BACKLOG = 'backlog'
STATUS_READY = 'ready'
STATUS_IN_PROGRESS = 'in-progress'
STATUS_REVIEW = 'review'
STATUS_BLOCKED = 'blocked'
STATUS_DONE = 'done'


@dataclass(eq=True, order=True)
class Board:
    id: int
    name: str = None
    description: str = None
    items: Set[Item] = None
    status_per_items: Dict[int, List[Item]] = None
    statuses: Tuple = None

    def __init__(self, id: int, name: str,
                 items: Set[Item],
                 description: str = None,
                 status_per_items: Dict[int, List[Item]] = None,
                 statuses: Tuple = None):
        self.id = id
        self.name = name
        self.items = items
        if not self.items:
            self.items = set()
        self.description = description
        self.status_per_items = status_per_items
        if not self.status_per_items:
            self.status_per_items = {}
        self.statuses = statuses
        if not self.statuses:
            self.statuses = (
                STATUS_BACKLOG, STATUS_READY, STATUS_IN_PROGRESS,
                STATUS_REVIEW, STATUS_BLOCKED, STATUS_DONE
            )

    def add(self, item: Item):
        if item in self.items:
            print('Already added')
            return
        self.items.add(item)
        self.status_per_items[item.id] = self.statuses[0]

    def remove(self, item: Item):
        self.items.remove(item)
        del self.status_per_items[item.id]

    def iterate(self):
        _list = list()
        queue = Queue()
        for item in self.items:
            if not item.previous_items:
                queue.put(item)
        while not queue.empty():
            itr = queue.get()
            if itr.next_items:
                for i in itr.next_items:
                    queue.put(i)
            _list.append(itr)
        return _list

    def status_incr(self, item: Item):
        assert item in self.items
        item_status = self.status_per_items[item.id]
        if item_status == STATUS_DONE:
            raise InvalidStatusError("Status is already done")
        curr_status_index = self.statuses.index(item_status)
        if item.previous_items:
            for prev in item.previous_items:
                st = self.status_per_items[prev.id]
                if st != STATUS_DONE and self.statuses.index(st) <= (
                curr_status_index + 1):
                    raise InvalidStatusError("Predecessor item still is "
                                             "not in advanced state")
        if item.next_items:
            for next in item.next_items:
                self.status_incr(next)

    def status_decr(self, item: Item):
        assert item in self.items
        item_status = self.status_per_items[item.id]
        curr_status_index = self.statuses.index(item_status)
        if curr_status_index == STATUS_BACKLOG:
            raise InvalidStatusError("Status is already at backlog")
        prev_status = self.statuses[curr_status_index - 1]
        if item.next_items:
            for next_item in item.next_items:
                st = self.status_per_items[next_item.id]
                if st != STATUS_BACKLOG and self.statuses.index(st) >= (
                    curr_status_index - 1
                ):
                    raise InvalidStatusError("Successor item not in "
                                             "further backwards state")


class InvalidStatusError(Exception):
    def __init__(self, msg):
        super(InvalidStatusError, self).__init__(f'Status Invalid Error: {msg}')

