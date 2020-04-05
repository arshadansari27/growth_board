from notion.block import PageBlock

from config import CONFIG, NOTION_TASKS_URL, NOTION_PROJECT_URL, \
    NOTION_QA_HIRING_URL, NOTION_BE_HIRING_URL
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
    update_from_hiring_board()


def update_from_hiring_board():
    task_db = NotionDB(CONFIG[NOTION_TASKS_URL])
    hiring_project_url = "https://www.notion.so/Hiring-4b932bc27b434d9d8700488acbc0f463"
    hiring_project = task_db.client.get_block(hiring_project_url)

    def setup(_task, board):
        title = f"[{board}] {_task.title}"
        print(f'[*] {title}')
        task_row = task_db.get_or_create(title)
        task_row.link = _task.get_browseable_url()
        task_row.project = hiring_project.id
        task_row.task_type = 'Story'
        task_row.link = _task.get_browseable_url()
        if getattr(_task, 'Schedule', None):
            task_row.scheduled = _task.Schedule
        if task.Status in {'Dropped', 'Offered'}:
            task_row.done = True
        else:
            task_row.done = False

    qa_board = NotionDB(CONFIG[NOTION_QA_HIRING_URL])
    be_board = NotionDB(CONFIG[NOTION_BE_HIRING_URL])
    for task in qa_board.get_all():
        if any(qa_board.client.current_user == u
                for u in task.Assign):
            setup(task, 'QA')
    for task in be_board.get_all():
        if any(be_board.client.current_user == u
                for u in task.Assign):
            setup(task, 'BE')


if __name__ == '__main__':
    update_tasks()
