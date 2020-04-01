from config import CONFIG
from notion_api import NotionDB



url = CONFIG["NOTION_TRACKING_DAILY_URL"]

TASK_GOAL_PROPERTY_MAP = {
    'goal': '@qm>',
    'description': '9iqC',
    'type': 'qrM3',
    'epic': '5fSo',
    'scheduled': 'WZBl',
    'status': ':tjE',
    'minor': '<4L(',
    'link': 'f$el',
    'init': '=tG;',
    'done': 'h,N?',
    'next': 'fQ&A',
    'waiting_on': 'WdYM',
    'dependents_finished': 'j)H^',
}

BOOKS_GOAL_PROPERTY_MAP = {
    'goals': '*fnW'
}

VIDEOS_GOAL_PROPERTY_MAP = {
    'goals': '&r0m'
}

db = NotionDB(url)
for p in db.view._get_record_data()['format'][
    'table_properties']:
    if p['visible']:
        print(p['property'])

