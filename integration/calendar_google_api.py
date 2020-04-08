import os
import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Union, List

import pytz
from dateutil import parser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import CONFIG, GOOGLE_CREDS_PERSONAL, GOOGLE_CREDS_OFFICE

PERSONAL = 'Personal'
OFFICE = 'Office'
SCOPES = ['https://www.googleapis.com/auth/calendar']
DEFAULT_TIMEZONE = 'Asia/Kolkata'
PERSONAL_PRIMARY = 'arshadansari27@gmail.com'
PERSONAL_NOTION = 'vftb34ce0qomud8pf3qh6d7r50@group.calendar.google.com'
OFFICE_NOTION = 'stockopedia.com_g9gordf54b2vm84uje4ptmqvhk@group.calendar.google.com'

@dataclass
class GoogleCalendarData:
    id: str
    name: str
    scheduled_start: Union[datetime, date] = None
    scheduled_end: Union[datetime, date] = None
    context:str = None
    status: str = None
    link: str = None
    description: str = None
    location: str = None
    created: datetime = None
    updated : datetime = None
    recurring: bool = False
    timezone: str = None

    def __repr__(self):
        return f"[{self.context}]: {self.name} ({self.scheduled_start} / " \
               f"{self.scheduled_end})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'scheduled_start': self.scheduled_start,
            'scheduled_end': self.scheduled_end,
            'context': self.context,
            'status': self.status,
            'link': self.link,
            'description': self.description,
            'location': self.location,
        }

    def to_google_event(self):
        # TODO: Order matters and it shouldn't
        if isinstance(self.scheduled_start, datetime):
            start = {
                'dateTime': self.scheduled_start.strftime(
                    '%Y-%m-%dT%H:%M:%S%z'),
                'timeZone': self.timezone,
            }
        elif isinstance(self.scheduled_start, date):
            start = {
                'date': self.scheduled_start.strftime('%Y-%m-%d'),
            }
        else:
            raise Exception("How can start date be none or any other thing?")
        if self.scheduled_end:
            if isinstance(self.scheduled_end, datetime):
                end = {
                    'dateTime': self.scheduled_end.strftime('%Y-%m-%dT%H:%M:%S%z'),
                    'timeZone': self.timezone,
                }
            elif isinstance(self.scheduled_end, date):
                end = {
                    'date': self.scheduled_end.strftime('%Y-%m-%d')
                }
            else:
                raise Exception("Not taking not date/datetime value for end")
        else:
            end = (start + timedelta(minutes=15)) if isinstance(start,
                                                                datetime) else start
        data = {
            'summary': self.name,
            'location': self.location,
            'description': self.description,
            'start': start,
            'end': end,
            'reminders': {
                'useDefault': True,
            },
        }
        if self.id:
            data['id'] = self.id
        return data

    @staticmethod
    def from_notion_task(task):
        return GoogleCalendarData(
            id=task.calendar_id,
            name=task.title,
            scheduled_start=task.scheduled.start,
            scheduled_end=task.scheduled.end,
            context=task.context,
            status='confirmed',
            link=task.calendar_link,
            description=task.summary,
            timezone=task.scheduled.timezone if task.scheduled.timezone else DEFAULT_TIMEZONE
        )

    def update_to_notion_dict(self):
        return {
            'start': self.scheduled_start,
            'end': self.scheduled_end,
            'timezone': self.timezone,
        }


class GoogleCalendar:
    def __init__(self, context, file_names):
        self.creds_path, token_file = file_names
        self.context = context
        print('[*] Ref file name for permission:', self.creds_path.replace('.json', '').split('-')[1])
        creds = None
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('calendar', 'v3', credentials=creds)

    def get_events(self, calendar_id, from_date=None, to_date=None):
        if not from_date:
            start = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
            start = (start - timedelta(days=30))
        else:
            start =  from_date.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
        if not to_date:
            end = (start + timedelta(days=365))
        else:
            end = to_date.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
                tzinfo=pytz.timezone('Asia/Kolkata')
            )
        time_min = start.isoformat()
        time_max = end.isoformat()
        t = self.service.events()
        events_result =  t.list(
                calendarId=calendar_id, timeMin=time_min,
                timeMax=time_max, singleEvents=True).execute()
        events = events_result.get('items', [])
        seen_recurring_events = {}
        for event in events:
            if event['status'] != 'confirmed':
                continue
            estart = event.get('start', {})
            eend = event.get('end', {})
            if not estart:
                raise Exception("There must be a start with or without an end")
            as_date_time = True if estart.get('dateTime') else False
            start = parser.parse(
                    estart.get('dateTime', estart.get('date')))
            end = parser.parse(
                    eend.get('dateTime', eend.get('date')))
            timezone = None
            if not as_date_time:
                start = start.date()
                end = end.date() if end else start.date()
            else:
                timezone = estart.get('timeZone', DEFAULT_TIMEZONE)
                start = start.replace(tzinfo=pytz.timezone(timezone))
                end = end.replace(tzinfo=pytz.timezone(timezone)) if end else start
            summary = event['summary']
            link = event['htmlLink']

            recurring = event.get('recurringEventId', False)
            data = GoogleCalendarData(
                event['id'],
                summary,
                scheduled_start=start,
                scheduled_end=end,
                link=link,
                context=self.context,
                status=event['status'],
                created=parser.parse(event['created']),
                updated = parser.parse(event['updated']),
                description=event.get('description'),
                location= event.get('location'),
                recurring=recurring,
                timezone=timezone
            )
            if recurring:
                if recurring not in seen_recurring_events:
                    rep = t.get(calendarId=calendar_id, eventId=event[
                        'recurringEventId']).execute()
                    check_recurrency_for_today(rep, data)
                    seen_recurring_events[recurring] = data
                continue
            yield data
        for data in seen_recurring_events.values():
            yield data

    def get_event(self, event_id, calendar_id):
        event = self.service.events().get(calendarId=calendar_id,
                                        eventId=event_id).execute()
        if not event:
            return None
        print('[*]', event)
        recurring = event.get('recurringEventId', False)
        estart = event.get('start', {})
        eend = event.get('end', {})
        if not estart:
            raise Exception("There must be a start with or without an end")
        as_date_time = True if estart.get('dateTime') else False
        start = parser.parse(
                estart.get('dateTime', estart.get('date')))
        end = parser.parse(
                eend.get('dateTime', eend.get('date')))
        timezone = None
        if not as_date_time:
            start = start.date()
            end = end.date() if end else start.date()
        else:
            timezone = estart.get('timeZone', DEFAULT_TIMEZONE)
            start = start.replace(tzinfo=pytz.timezone(timezone))
            end = end.replace(tzinfo=pytz.timezone(timezone)) if end else start
        return GoogleCalendarData(
                event['id'],
                event['summary'],
                scheduled_start=start,
                scheduled_end=end,
                link=event['htmlLink'],
                context=self.context,
                status=event['status'],
                created=parser.parse(event['created']),
                updated = parser.parse(event['updated']),
                description=event.get('description'),
                location= event.get('location'),
                recurring=recurring,
                timezone=timezone
            )

    def create_event(self, event: GoogleCalendarData, calendar_id):
        assert not event.id
        cal_event = event.to_google_event()
        print('Inserting', cal_event)
        event_dict = self.service.events().insert(calendarId=calendar_id,
                                           body=cal_event).execute()
        event.id = event_dict['id']
        return event

    def update_event(self, event: GoogleCalendarData, calendar_id):
        cal_event = event.to_google_event()
        print('Updating', cal_event)
        self.service.events().update(calendarId=calendar_id,
                                     eventId=event.id, body=cal_event).execute()
        return event

    def delete_event(self, event_id, calendar_id):
        self.service.events().delete(calendarId=calendar_id,
                                     eventId=event_id).execute()

    def list_calendars(self):
        lst = self.service.calendarList().list().execute()
        for l_e in lst['items']:
            print(l_e['id'], l_e['summary'], l_e['timeZone'])

    @property
    def token(self):
        return f'token-{self.context}.pickle'


def check_recurrency_for_today(event_resp, event: GoogleCalendarData):
    def update_to_today():
        event.scheduled_start = event.scheduled_start.replace(
                year=today.year, month=today.month, day=today.day)
        if event.scheduled_end:
            event.scheduled_end = event.scheduled_end.replace(
                    year=today.year, month=today.month, day=today.day)
    recurrence = event_resp['recurrence']
    rec = recurrence[0].replace('RRULE:', '').split(';')
    frequency = None
    days = None
    for r in rec:
        if 'FREQ' in r:
            frequency = r.split('=')[1]
        if 'BYDAY' in r:
            days = [WEEKDAY[u] for u in r.split('=')[1].split(',')]
    today = datetime.today()
    if frequency == 'DAILY':
        update_to_today()
        return event
    elif frequency == 'WEEKLY' and not days:
        week_day = event.scheduled_start.weekday()
        if week_day == today.weekday():
            update_to_today()
    elif frequency == 'WEEKLY' and today.weekday() in days:
        update_to_today()
    return event


WEEKDAY = {
    'MO': 0,
    'TU': 1,
    'WE': 2,
    'TH': 3,
    'FR': 4,
    'SA': 5,
    'SU': 6
}

if __name__ == '__main__':
    p_calendar = GoogleCalendar(PERSONAL, CONFIG[GOOGLE_CREDS_PERSONAL])
    from_date = datetime.today() - timedelta(days=7)
    to_date = datetime.today() + timedelta(days=7)
    print('\n'.join(str(u) for u in p_calendar.get_events('primary', from_date,
                                                 to_date)))
