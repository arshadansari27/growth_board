from growth.config import CONFIG
from growth.integration import update_study

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

def update_from_clickup():
    relative_attributes = {
        'List Name',
        'Task Name',
        'Tags',
    }
    categories = set()
    for tid, task in ALL_TASKS.items():
        if task['Space Name'] != 'Goals':
            continue
        task[TAGS] = untag(task[TAGS])
        tags = task[TAGS]
        if not any(u in tags for u in {'book', 'course'}):
            continue
        _task = sorted([
            (u,  v) for u, v in task.items()
            if u in relative_attributes])
        task_dict = dict(_task)
        category = task_dict['List Name']
        tag = 'book' if 'book' in tags else 'course'
        name = task_dict['Task Name']
        yield (name, tag, category)


def untag(tags):
    return [u for u in tags.replace('[', '').replace(']', '').split(',') if u]


if __name__ == '__main__':
    update_study(update_from_clickup())
