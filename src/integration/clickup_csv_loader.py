from config import CONFIG
from integration.notion_api import update_projects_and_tasks
from dateutil import parser

FILE = '/Users/arshad/Desktop/clickup.csv'
import csv

T_ID = 'Task ID'
TASK = 'Task Name'
STATUS = 'Status'
DATE_DUE = 'Due Date Text'
DATE_START = 'Start Date Text'
PARENT = 'Parent ID'
PRIORITY = 'Priority'
LIST = 'List Name'
PROJECT = 'Project Name'
SPACE = "Space Name"
TAGS = 'Tags'
CARE_ABOUT_ATTRS = {
T_ID, TASK, STATUS, DATE_DUE, DATE_START, PARENT, PRIORITY, LIST, PROJECT,
    SPACE, TAGS
}

ALL_TASKS = {}

with open(FILE) as csv_file:
    reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
    for read in reader:
        n_dict = {u: v if v != 'null' else None for u, v in read.items() if u
                  in
                  CARE_ABOUT_ATTRS}
        ALL_TASKS[n_dict[T_ID]] = n_dict

def get_projects_and_tasks():
    for tid, task in ALL_TASKS.items():
        if task[PARENT] or task[SPACE] != 'Projects & Tasks':
            continue
        due_date = parser.parse(task[DATE_DUE]) if task[DATE_DUE] else None
        start_date = parser.parse(task[DATE_START]) if task[DATE_START] else None
        tags = untag(task[TAGS])
        yield (
            task[TASK],
            task[LIST],
            task[PROJECT],
            task[STATUS],
            due_date if (due_date or start_date) else None,
            start_date if (due_date or start_date) else None,
            tags,
        )


def untag(tags):
    return [u for u in tags.replace('[', '').replace(']', '').split(',') if u]


if __name__ == '__main__':
    link = CONFIG['NOTION_CLICKUP_URL']
    update_projects_and_tasks([u for u in get_projects_and_tasks()], link)