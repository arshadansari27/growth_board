from datetime import datetime, date

import pytz
from notion.collection import NotionDate
from icalendar import Calendar, Event
from config import CONFIG, GOOGLE_CREDS_PERSONAL, GOOGLE_CREDS_OFFICE, \
    NOTION_TASKS_URL
from integration.calendar_google_api import GoogleCalendar
from notion_api import NotionDB

task_db = NotionDB(CONFIG[NOTION_TASKS_URL])


def create_calendar_from_tasks():
    def create_summary(task):
        title = task.title
        context = f' @ {task.context}' if task.context else ''
        return f"{title}{context}"

    def create_description(task):
        summary = f' ({task.summary})' if task.summary else task.title
        if task.link:
            summary = f'<a href="{task.link}">{summary}</a>'
        return summary

    def to_date_time(_date):
        if isinstance(_date, datetime):
            dt = _date
        elif isinstance(_date, date):
            dt = datetime(_date.year, _date.month, _date.day)
        else:
            raise Exception(f"What the hell! {_date}, {type(_date)}")
        return dt.replace(tzinfo=pytz.FixedOffset(330))

    calendar = Calendar()
    for task in task_db.get_all():
        if not task.scheduled or task.done or task.task_type == 'Event':
            continue
        event = Event()
        event['uid'] = str(task.id)
        event.add('dtstart', to_date_time(task.scheduled.start))
        if task.scheduled.end:
            event.add('dtend', to_date_time(task.scheduled.end))
        event['summary'] = create_summary(task)
        event['description'] = create_description(task)
        calendar.add_component(event)
    return calendar.to_ical()


def update_notion():
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

