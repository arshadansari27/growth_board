from datetime import datetime, date, timedelta

import pytz
from notion.collection import NotionDate
from icalendar import Calendar, Event
from config import CONFIG, GOOGLE_CREDS_PERSONAL, GOOGLE_CREDS_OFFICE, \
    NOTION_TASKS_URL
from integration.calendar_google_api import GoogleCalendar
from notion_api import NotionDB


def create_calendar_from_tasks():
    task_db = NotionDB(CONFIG[NOTION_TASKS_URL])

    def create_summary(task):
        title = task.title
        context = f' @ {task.context}' if task.context else ''
        return f"{title}{context}"

    def create_description(task):
        summary = f' ({task.summary})' if task.summary else task.title
        if task.link:
            summary = f'<a href="{task.link}">{summary}</a>'
        return summary

    def ensure_datetime(dt):
        if isinstance(dt, date):
            dt = datetime(dt.year, dt.month, dt.day)
        return dt

    def ensure_date(dt):
        if isinstance(dt, datetime):
            return dt.date()
        return dt

    def to_date_time(start_date, end_date):
        if end_date and ensure_date(start_date) != ensure_date(end_date):
            return ensure_date(start_date), ensure_date(end_date)
        if isinstance(start_date, datetime):
            if not end_date:
                end_date = start_date + timedelta(seconds=1800)
            else:
                end_date = ensure_datetime(end_date)
            return start_date, end_date
        return ensure_date(start_date), ensure_date(end_date)

    calendar = Calendar()
    for task in task_db.get_all():
        if not task.scheduled or task.done or task.task_type == 'Event':
            continue
        event = Event()
        print("[*]", task.title)
        event['uid'] = str(task.id)
        start, end = to_date_time(task.scheduled.start, task.scheduled.end)
        event.add('dtstart', start)
        if end:
            event.add('dtend', end)
        event['summary'] = create_summary(task)
        event['description'] = create_description(task)
        calendar.add_component(event)
    return calendar.to_ical()


def update_notion():
    task_db = NotionDB(CONFIG[NOTION_TASKS_URL])
    for event in calendar_events():
        update_event(task_db, event)


def update_event(task_db, event):
    summary, start, end, link, context, merged = event
    row = task_db.get_or_create(summary)
    row.scheduled = NotionDate(start=start, end=end)
    row.link = link
    row.parent_name = 'Google Calendar'
    row.type = 'Event'
    row.context = context
    if merged and row.done:
        row.done = False
    print("Added row = ", row.title)


def calendar_events():
    p_calendar = GoogleCalendar('Personal', CONFIG[GOOGLE_CREDS_PERSONAL])
    o_calendar = GoogleCalendar('Office', CONFIG[GOOGLE_CREDS_OFFICE])
    events = []
    events.extend(list(p_calendar.get_current_events()))
    events.extend(list(o_calendar.get_current_events()))
    return sorted(events, key=lambda u: u[1])


if __name__ == '__main__':
    update_notion()

