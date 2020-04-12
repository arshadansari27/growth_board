from datetime import datetime, timedelta

from .. import Due
from ..tasks import Project, Task, Milestone


def test_project_milestone_and_tasks():
    due = Due(datetime.now(), (datetime.now() + timedelta(days=30)))
    projects = [
        Project('1', 'test-project-1', due=due),
        Project('2', 'test-project-2', due=due),
    ]
    milestones = [Milestone(f'{i + 1}', f'test-milestone-{i + 1}', projects[i % len(projects)]) for i in range(4)]
    milestones.append(None)
    milestones.append(None)

    tasks = [Task(
                f'{i + 1}',
                f'test-task-{i + 1}',
                due=due,
                project=projects[i % len(projects)],
                milestone=milestones[i % len(milestones)])
            for i in range(10)]

    for task in tasks:
        assert task.uuid is not None and task.project is not None
        assert task in task.project.tasks
        if task.milestone:
            assert task in task.milestone.tasks
