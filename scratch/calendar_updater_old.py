from datetime import datetime, date, timedelta

import pytz
from notion.collection import NotionDate
from icalendar import Calendar, Event
from config import CONFIG, GOOGLE_CREDS_PERSONAL, GOOGLE_CREDS_OFFICE, \
    NOTION_TASKS_URL
from integration.calendar_google_api import GoogleCalendar, GoogleCalendarData, \
    PERSONAL_NOTION, OFFICE_NOTION, OFFICE, PERSONAL
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


def update_calendar_times():

    task_db = NotionDB(CONFIG[NOTION_TASKS_URL])
    p_calendar = GoogleCalendar(PERSONAL, CONFIG[GOOGLE_CREDS_PERSONAL])
    o_calendar = GoogleCalendar(OFFICE, CONFIG[GOOGLE_CREDS_OFFICE])
    all_events = {}
    all_tasks = {}

    def update_tasks(name):
        task = task_db.get_or_create(name)
        event = all_events[name]
        task.scheduled.start = event.scheduled_start
        task.scheduled.end = event.scheduled_end
        task.calendar_link = event.link
        task.context = event.context
        if event.description:
            task.summary = event.description
        if event.recurring:
            task.done = False

    def update_calendar(name):
        task = task_db.get_or_create(name)
        if name not in all_events:
            event = GoogleCalendarData(
                task.title,
                task.scheduled.start,
                task.scheduled.end,
                task.context,
                'confirmed',
                None,
                task.summary,
            )
            method = 'create_event'
        else:
            event = all_events[name]
            event.name = task.title
            event.scheduled_start = task.scheduled.start
            event.scheduled_end = task.scheduled.end
            event.description = task.scheduled.description
            event.context = task.context
            event.status = 'confirmed'
            method = 'update_event'

        if task.context == PERSONAL:
            event = getattr(p_calendar, method)(event, 'primary')
        elif task.context == OFFICE:
            event = getattr(o_calendar, method)(event, 'primary')
        else:
            raise Exception(f"Invalid context {task.context}")
        task.calendar_link = event.id

    all_tasks.update({task.title: task for task in task_db.get_all() if
     task.scheduled and not
     task.done})
    all_events.update({e.name: e
                       for e in list(
                        p_calendar.get_events())})
    all_events.update({e.name: e
                     for e in list(
                        o_calendar.get_events())})
    tasks_to_add, events_to_add = get_updatable_entities(all_tasks, all_events)
    for name in tasks_to_add:
        update_tasks(name)
    for name in events_to_add:
        update_calendar(name)


def get_updatable_entities(tasks, events):
    def same_date(date1, date2):
        if type(date1) != type(date2):
            return False
        if isinstance(date1, datetime) and isinstance(date2, datetime):
            date1 = date1.replace(tzinfo=pytz.FixedOffset(330))
            date2 = date2.replace(tzinfo=pytz.FixedOffset(330))
        return date1 == date2

    def cmp(_event, _task):
        if _event.name != _task.title:
            return False
        if not same_date(_event.scheduled_start, _task.scheduled.start):
            return False
        if not same_date(_event.scheduled_end, _task.scheduled.end):
            return False
        return True

    def is_event_updated_later(_task, _event):
        event_updated = _event.updated.replace(tzinfo=pytz.FixedOffset(330))
        task_updated = _task.updated.replace(tzinfo=pytz.FixedOffset(330))
        if event_updated > task_updated:
            return True
        return False

    task_set = set(tasks.keys())
    event_set = set(events.keys())
    exists_on_both = task_set.intersection(event_set)
    exists_on_task_only = task_set.difference(event_set)
    exists_on_event_only = event_set.difference(task_set)
    add_to_tasks = []
    add_to_calendar = []
    for name in exists_on_both:
        task = tasks[name]
        event = events[name]
        if cmp(events[name], tasks[name]):
            continue
        if is_event_updated_later(task, event):
            add_to_tasks.append(name)
        else:
            add_to_calendar.append(name)
    for name in exists_on_task_only:
        add_to_calendar.append(name)
    for name in exists_on_event_only:
        add_to_tasks.append(name)
    return add_to_tasks, add_to_calendar


def update_notion():
    task_db = NotionDB(CONFIG[NOTION_TASKS_URL])
    for event in calendar_primary_events():
        update_event(task_db, event)


def update_event(task_db, event):
    summary, start, end, link, context, merged = event
    row = task_db.get_or_create(summary)
    row.scheduled = NotionDate(start=start, end=end)
    if not row.link:
        row.link = link
    if not row.parent_name:
        row.parent_name = 'Google Calendar'
    if not row.task_type:
        row.type = 'Event'
    if not row.context:
        row.context = context
    if merged and row.done:
        row.done = False


def calendar_primary_events():
    p_calendar = GoogleCalendar('Personal', CONFIG[GOOGLE_CREDS_PERSONAL])
    o_calendar = GoogleCalendar('Office', CONFIG[GOOGLE_CREDS_OFFICE])
    events = []
    events.extend(list(p_calendar.get_current_events()))
    events.extend(list(o_calendar.get_current_events()))
    return sorted(events, key=lambda u: u[1])


if __name__ == '__main__':
    #update_notion()
    update_calendar_times()
    '''
    print(CONFIG)
    o_calendar = GoogleCalendar(OFFICE, CONFIG[GOOGLE_CREDS_OFFICE])
    print(o_calendar.list_calendars())
    evt = None
    for e in list(p_calendar.get_events(PERSONAL_NOTION)):
        print(e.name, e.created, e.updated, e.scheduled_start,
              e.scheduled_end, e.description, e.status, e.link, e.location)
        evt = e
    '''
    #evt.name = 'testing 2'
    #evt.scheduled_start = datetime.now() + timedelta(minutes=60)
    #evt.scheduled_end = evt.scheduled_start + timedelta(minutes=90)
    #p_calendar.create_event(evt, PERSONAL_NOTION)
