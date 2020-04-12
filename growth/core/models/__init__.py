from dataclasses import dataclass
from queue import Queue
from typing import Set, Any


class AlreadyDoneError(Exception):
    def __init__(self, f):
        super(AlreadyDoneError, self).__init__(f"Already done {f}")


@dataclass(eq=True, order=True)
class Item:
    element: Any
    next_items: Set["Item"]
    previous_items: Set["Item"]

    def __init__(self, element: Any,
                 next_items: Set["Item"] = None,
                 previous_items: Set["Item"] = None):
        self.element = element
        self.next_items = next_items if next_items else set()
        self.previous_items = previous_items if previous_items else set()

    def _check_cycle(self, item, attr):
        queue = Queue()
        queue.put(item)
        while not queue.empty():
            p = queue.get()
            assert self != p, f'Cyclic dependency error [{item}]'
            items = getattr(p, attr, set())
            if not items:
                continue
            for n in items:
                queue.put(n)

    def add_next(self, next_item: "Item"):
        if next_item in self.next_items:
            return
        self._check_cycle(next_item, 'next_items')
        next_item.add_previous(self)
        self.next_items.add(next_item)

    def add_previous(self, previous_item: "Item"):
        if previous_item in self.previous_items:
            return
        self._check_cycle(previous_item, 'previous_items')
        self.previous_items.add(previous_item)
        previous_item.add_next(self)

    def remove_next(self, next_item: "Item"):
        if next_item in self.next_items:
            self.next_items.remove(next_item)
        if self in next_item.previous_items:
            next_item.previous_items.remove(self)

    def remove_previous(self, previous_item: "Item"):
        if previous_item in self.previous_items:
            self.previous_items.remove(previous_item)
        if self in previous_item.next_items:
            previous_item.next_items.remove(self)


