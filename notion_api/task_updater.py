from config import CONFIG, NOTION_TASKS_URL, NOTION_PROJECT_URL
from integration.jira_api import update_notion_jira_tasks
from notion_api import NotionDB



def update_tasks():
    task_db = NotionDB(CONFIG[NOTION_TASKS_URL])
    project_db = NotionDB(CONFIG[NOTION_PROJECT_URL])
    update_notion_jira_tasks(task_db, project_db)
    for task in task_db.get_all():
        if task.done:
            task.status = 'Done'
        if task.parent_name and not task.parent_task:
            parent_task = task_db.get_or_create(task.parent_name)
            task.parent_task = parent_task

if __name__ == '__main__':
    update_tasks()