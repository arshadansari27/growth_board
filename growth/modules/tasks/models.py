from growth.commons import STATUSES, TODO, NEXT, IN_PROGRESS, REVIEW, DONE, Objective


@dataclass
class TaskList:
    id: int
    name: str
    description: str = None


@dataclass(eq=True, order=True)
class Task:
    id: int
    name: str
    status: str
    task_lists: List[TaskList]
    description: str = None
    scheduled_start: datetime = None
    scheduled_end: datetime = None
    link: str = None
    progress: int = None
    priority: int = None
    tags: List[str] = None
    milestone: "Milestone" = None

