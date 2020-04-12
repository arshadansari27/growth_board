from typing import List, Set

from . import Due


class Project:
    def __init__(
            self, uuid: int, name: str, completed: bool = None,
            archived: bool = None, due: Due = None,
            milestones: Set["Milestone"] = None,
            tasks: Set["Task"] = None,
            description: str = None):
        self.uuid = uuid
        self.name = name
        if not tasks:
            self.tasks = set()
        else:
            self.tasks = tasks
        if not milestones:
            self.milestones = set()
        else:
            self.milestones = milestones
        self.completed = completed
        self.archived = archived
        self.due = due
        self.description = description

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False
        return self.uuid == other.uuid

    @property
    def progress(self):
        return sum(1.0 for i in self.tasks if i.completed) / len(self.tasks)


class Milestone:
    def __init__(
            self, uuid: int, name: str, project: Project, completed: bool = None,
            due: Due = None, tasks: List["Task"] = None, description: str = None):
        self.uuid = uuid
        self.name = name
        self.project = project
        assert self.project is not None, f"{self}'s project is None!"
        self.project.milestones.add(self)
        if not tasks:
            self.tasks = set()
        else:
            self.tasks = tasks
        self.completed = completed
        self.due = due
        self.description = description

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False
        return self.uuid == other.uuid

    @property
    def progress(self):
        return sum(1.0 for i in self.tasks if i.completed) / len(self.tasks)


class Task:
    def __init__(
            self, uuid: int, name: str, project: Project,
            milestone: Milestone = None, status: str = None,
            completed: bool = None, due: Due = None, priority: int = None,
            description: str = None, progress: int = None,
            tags: List[str] = None, icon: str = None):
        self.uuid = uuid
        self.name = name
        self.project = project
        assert self.project is not None, f"{self}'s project is None!"
        self.project.tasks.add(self)
        self.milestone = milestone
        self.status = status
        self.due = due
        self.description = description
        self.progress = progress
        self.priority = priority
        self.icon = icon
        self.tags = tags
        self.completed = completed
        if self.milestone:
            self.milestone.tasks.add(self)

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return self.uuid == other.uuid

