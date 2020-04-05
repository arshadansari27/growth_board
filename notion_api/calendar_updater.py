from datetime import date, datetime
from sys import stdout

import pytz
from notion.collection import NotionDate

from config import CONFIG, GOOGLE_CREDS_PERSONAL, GOOGLE_CREDS_OFFICE, \
    NOTION_TASKS_URL
from integration.calendar_google_api import GoogleCalendar, \
    GoogleCalendarData, \
    PERSONAL_NOTION, OFFICE_NOTION, OFFICE, PERSONAL, DEFAULT_TIMEZONE
from notion_api import NotionDB


def update_calendar_times():

    task_db = NotionDB(CONFIG[NOTION_TASKS_URL])
    p_calendar = GoogleCalendar(PERSONAL, CONFIG[GOOGLE_CREDS_PERSONAL])
    o_calendar = GoogleCalendar(OFFICE, CONFIG[GOOGLE_CREDS_OFFICE])
    all_events = {}
    all_tasks = {}

    def get_calendar_by_context(context):
        if context == PERSONAL:
            return (p_calendar, PERSONAL_NOTION)
        elif context == OFFICE:
            return (o_calendar, OFFICE_NOTION)
        raise Exception(f"Invalid context provided: {context}")

    key_gen = lambda c, u: f"{c}-{u}"

    all_tasks.update({task.title: task for task in task_db.get_all() if
                      task.scheduled})
    all_events.update({key_gen(e.context, e.id): e for e in
                       p_calendar.get_events(PERSONAL_NOTION)})

    all_events.update({key_gen(e.context, e.id): e for e in
                       o_calendar.get_events(OFFICE_NOTION)})
    for task in all_tasks.values():
        calendar, calendar_id = get_calendar_by_context(task.context)
        event_key = key_gen(task.context, task.calendar_id)
        if task.done and task.calendar_id:
            all_events.pop(event_key)
            continue
        try:
            if not task.calendar_id:
                print(f"[{task.name}] Creating new event")
                created_event = create_calendar_event(task, calendar, calendar_id)
                task.calendar_id = created_event.id
            else:
                print(f"[{task.name}] Checking existing")
                event = all_events.get(event_key)
                stdout.flush()
                update_calendar_or_notion(task, event, calendar, calendar_id)
        except:
            print(task.title, all_events.get(event_key))
            raise


def create_calendar_event(task, calendar, calendar_id):
    event = GoogleCalendarData.from_notion_task(task)
    return calendar.create_event(event, calendar_id)


def update_calendar_or_notion(task, event, calendar, calendar_id):
    if cmp(event, task):
        print(f"[\t] Skipping")
        return
    if is_event_updated_later(task, event) is 1:
        print(f"[\t] Task")
        update_data = event.update_to_notion_dict()
        task.scheduled = NotionDate(start=update_data['start'], end=update_data[
                'end'], timezone=DEFAULT_TIMEZONE)
        return event
    else:
        print(f"[\t] Event")
        event.scheduled_start = task.scheduled.start
        event.scheduled_end = task.scheduled.end
        event.timezone = DEFAULT_TIMEZONE
        return calendar.update_event(event, calendar_id)


def cmp(_event, _task):
    if _event.name != _task.title:
        return False
    if not same_date(_event.scheduled_start, _task.scheduled.start,
                     _task.scheduled.timezone):
        return False
    if _event.scheduled_start == _event.scheduled_end and not \
            _task.scheduled.end:
        return True
    if not same_date(_event.scheduled_end, _task.scheduled.end,
                     _task.scheduled.timezone):
        return False
    return True


def same_date(date1, date2, _timezone):
    if type(date1) != type(date2):
        return False
    if isinstance(date1, datetime) and isinstance(date2, datetime):
        date1 = date1.replace(tzinfo=None)
        date2 = date2.replace(tzinfo=None)
    if date1 != date2:
        return False
    return True


def is_event_updated_later(task, event):
    timezone = task.scheduled.timezone  if task.scheduled.timezone else DEFAULT_TIMEZONE
    event_updated = event.updated.replace(tzinfo=pytz.timezone(timezone))
    task_updated = task.updated.replace(tzinfo=pytz.timezone(timezone))
    if event_updated > task_updated:
        return 1
    elif task_updated < event_updated:
        return -1
    return 0


if __name__ == '__main__':
    update_calendar_times()
