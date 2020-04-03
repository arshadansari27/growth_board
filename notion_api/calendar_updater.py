from notion.collection import NotionDate

from config import CONFIG, GOOGLE_CREDS_PERSONAL, GOOGLE_CREDS_OFFICE, \
    NOTION_TASKS_URL
from integration.calendar_google_api import GoogleCalendar
from notion_api import NotionDB

task_db = NotionDB(CONFIG[NOTION_TASKS_URL])


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

