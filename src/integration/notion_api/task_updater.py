from typing import Callable, List

from config import CONFIG
from integration.notion_api import NotionDB


def update_tasks(external_loaders: List[Callable]):
    task_db = NotionDB(CONFIG['NOTION_TASKS_URL'])

    for loaders in external_loaders:
        loaders()

    for task in task_db.get_all():
        if not task.status and not task.done:
            task.status = 'Backlog'
        if task.done:
            task.status = 'Done'
        if task.parent_name and not task.parent_task:
            parent_task = task_db.get_or_create(task.parent_name)
            task.parent_task = parent_task

if __name__ == '__main__':
    update_tasks([])