GOAL_TYPE_LONG = "long-term"
GOAL_TYPE_SHORT = "short-term"


@dataclass(eq=true, order=true)
class Goal:
    id: int
    name: str
    description: str
    scheduled_start: datetime
    scheduled_end: datetime
    stat: float
    goal_type: str
    next: List["Goal"]
    previous: List["Goal"]


@dataclass(eq=true, order=true)
class Project(Goal):
    task_list: "TaskList"


@dataclass(eq=true, order=true)
class Milestone(Project):
    task_list: "TaskList"
    project: Project
