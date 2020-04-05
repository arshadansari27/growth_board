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

from config import CONFIG, GOOGLE_CREDS_PERSONAL

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
        return f"[{self.context}]: {self.name} ({self.id})"

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

    def get_events(self, calendar_id) -> List[GoogleCalendarData]:
        start = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0)
        start = (start - timedelta(days=30))
        end = (start + timedelta(days=365))
        time_min = start.isoformat() + 'Z'
        time_max = end.isoformat() + 'Z'
        t = self.service.events()
        events_result =  t.list(
                calendarId=calendar_id, timeMin=time_min,
                timeMax=time_max, singleEvents=True).execute()
        events = events_result.get('items', [])
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
                    eend.get('dateTime', estart.get('date')))
            timezone = None
            if not as_date_time:
                start = start.date()
                end = end.date()
            else:
                timezone = estart.get('timeZone', DEFAULT_TIMEZONE)
                start = start.replace(tzinfo=pytz.timezone(timezone))
                end = end.replace(tzinfo=pytz.timezone(timezone))

            recurring = True if event.get('recurringEventId', None) else False
            if recurring and not (start.date() if as_date_time else start) == date.today():
                continue
            summary = event['summary']
            link = event['htmlLink']
            yield GoogleCalendarData(
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

    def list_calendars(self):
        lst = self.service.calendarList().list().execute()
        for l_e in lst['items']:
            print(l_e['id'], l_e['summary'], l_e['timeZone'])

    @property
    def token(self):
        return f'token-{self.context}.pickle'


