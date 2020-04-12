TODO, NEXT, IN_PROGRESS, REVIEW, DONE = 'To Do', 'Next', 'In Progress', 'Review', 'Done'
STATUSES = {TODO, NEXT, IN_PROGRESS, REVIEW, DONE}


@dataclass
class Objective:
    id: int
    name: str
    description: str = None
    scheduled_start: datetime = None
    scheduled_end: datetime = None
    stat: float = None

    @property
    def is_time_bound(self):
        return self.scheduled_start and self.scheduled_end

    def __repr__(self):
        return f"([{self.id}] {self.name})"

    def __hash__(self):
        return self._check(other) and hash(self.id)

    def __le__(self, other: "Task"):
        return self._check(other) and self.scheduled_start <= other.scheduled_start

    def __lt__(self, other: "Task"):
        return self._check(other) and self.scheduled_start < other.scheduled_start

    def __ge__(self, other: "Task"):
        return self._check(other) and self.scheduled_start >= other.scheduled_start

    def __gt__(self, other: "Task"):
        return self._check(other) and self.scheduled_start > other.scheduled_start

    def __eq__(self, other: "Task"):
        return self._check(other) and self.id == other.id


def _check(other: "Task"):
    return isinstance(other, Task)

