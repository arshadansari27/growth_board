from collections import defaultdict
from datetime import date, datetime, timedelta

from config import NOTION_TRACKABLE_THINGS_URL, NOTION_TRACKING_DAILY_URL, \
    CONFIG, NOTION_TRACKING_WEEKLY_URL, NOTION_TASKS_URL
from notion_api import NotionDB


def update_daily_tracker_from_tasks():
    today = date.today()
    daily_tracker_db = NotionDB(CONFIG[NOTION_TRACKING_DAILY_URL])
    tasks_db = NotionDB(CONFIG[NOTION_TASKS_URL])
    trackable_things_db = NotionDB(CONFIG[NOTION_TRACKABLE_THINGS_URL])
    for trackable_things in trackable_things_db.get_all():
        task_name = getattr(trackable_things, 'tasks_name')
        if not trackable_things.boolean_add:
            print(f"Skipping as {task_name} is not boolean")
            continue
        if not task_name:
            print("Skipping as task name is not matched")
            continue
        task = tasks_db.get(task_name)
        if not task:
            print("Skipping the task", task_name)
            continue
        start_date = task.scheduled.start
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if not task.done:
            print("Skipping the task not done", task.title)
            continue
        daily_tracked = daily_tracker_db.get(start_date.strftime("%b %d"))
        if not daily_tracked:
            print("Skipping the task as not on daily_tracked", task.title)
            continue
        print("Setting", trackable_things.title, task.done)
        setattr(daily_tracked, trackable_things.title, task.done)


def update_tracker():
    today = date.today()
    tracker_schema_rows = update_tracker_schema(today)
    weekly_tracker_db = NotionDB(CONFIG[NOTION_TRACKING_WEEKLY_URL])
    daily_tracker_db = NotionDB(CONFIG[NOTION_TRACKING_DAILY_URL])
    weeks = {week.id: week for week in weekly_tracker_db.get_all()}
    current_dict = defaultdict(list)
    previous_dict = defaultdict(list)
    for row in daily_tracker_db.rows.values():
        week_id = row.Week[0].id
        week = weeks[week_id]
        if _is_current_week(today, week):
            _dict_to_update = current_dict
        elif _is_previous_week(today, week):
            _dict_to_update = previous_dict
        else:
            continue
        property_slugs = row._get_property_slugs()
        for property_slug in property_slugs:
            if property_slug in {'title', 'name', 'date', 'week', 'final'}:
                continue
            _dict_to_update[property_slug].append(getattr(row, property_slug, 0))
    for title, tracker_schema_row in tracker_schema_rows.items():
        print("*** Updating", title)
        current_info = current_dict[title]
        boolean_add = tracker_schema_row.boolean_add
        current_agg = calculate(current_info, boolean_add)
        previous_info = previous_dict[title]
        previous_agg = calculate(previous_info, boolean_add)
        tracker_schema_row.current_agg = current_agg
        tracker_schema_row.previous_agg = previous_agg


def update_tracker_schema(today: date):
    today_title = today.strftime("%b %d")
    daily_tracker_db = NotionDB(CONFIG[NOTION_TRACKING_DAILY_URL])
    trackable_things_db = NotionDB(CONFIG[NOTION_TRACKABLE_THINGS_URL])
    row = daily_tracker_db.get(today_title)
    if not row:
        raise Exception("Not the right time to be doing this!")
    property_slugs = row._get_property_slugs()
    for property_slug in property_slugs:
        if property_slug in {'title', 'name', 'date', 'week', 'final'}:
            continue
        r = trackable_things_db.get_or_create(property_slug)
        if not r.boolean_add and type(getattr(row, property_slug, None)) == bool:
            r.boolean_add = True
    return {u.title: u for u in trackable_things_db.get_all()}


def calculate(data, boolean_add):
    agg_total = len(data)
    if boolean_add:
        agg_value = sum(1 for i in data if i)
    else:
        agg_value = sum(i for i in data if i is not None)
    return round(float(agg_value) / agg_total, 2)


def _is_current_week(today: date, week):
    today = _ensure_date(today)
    start = _ensure_date(week.Week.start)
    end = _ensure_date(week.Week.end)
    return start <= today <= end


def _is_previous_week(today: date, week):
    today = _ensure_date(today)
    end = _ensure_date(week.Week.end)
    return today > end and today <= (end + timedelta(days=7))


def _ensure_date(value):
    if isinstance(value, datetime):
        value = value.date()
    return value

if __name__ == '__main__':
    update_daily_tracker_from_tasks()
