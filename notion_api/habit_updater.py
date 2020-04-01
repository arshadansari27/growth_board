from collections import defaultdict
from datetime import datetime, timedelta

from config import CONFIG, NOTION_TASKS_URL, NOTION_PROJECT_URL, \
    NOTION_HABIT_ROUTINE_URL, NOTION_TRACKING_DAILY_URL
from integration.jira_api import update_notion_jira_tasks
from notion_api import NotionDB


def update_habits():
    habits_db = NotionDB(CONFIG[NOTION_HABIT_ROUTINE_URL])
    keys = list(habits_db.rows.keys())
    tracker_db = NotionDB(CONFIG[NOTION_TRACKING_DAILY_URL])
    client = tracker_db.client
    today = datetime.now().date()
    previous_habits = defaultdict(list)
    current_habits = defaultdict(list)
    for row in tracker_db.rows.values():
        week_id = row.Week[0].id
        week = client.get_block(week_id)
        current = week.Week.start < today < week.Week.end
        previous = today > week.Week.end and (today < (datetime.now() +
                   timedelta(days=8)).date())
        if not current and not previous:
            continue
        for k in keys:
            v = 1 if getattr(row, k, None) else 0
            if current:
                current_habits[k].append(v)
            if previous:
                previous_habits[k].append(v)
    for k in keys:
        habit = habits_db.get_or_create(k)
        habit.Status = sum(current_habits[k]) / len(current_habits[k])
        habit.StatusPrev = sum(previous_habits[k]) / len(previous_habits[k])


if __name__ == '__main__':
    update_habits()