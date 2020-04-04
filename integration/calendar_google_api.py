import os
import pickle
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, date

import pytz
from dateutil import parser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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
    scheduled_start: datetime = None
    scheduled_end: datetime = None
    context:str = None
    status: str = None
    link: str = None
    description: str = None
    location: str = None
    created: datetime = None
    updated : datetime = None
    recurring: bool = False

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
        return {
            'summary': self.name,
            'location': self.location,
            'description': self.description,
            'start': {
                'dateTime': self.scheduled_start.strftime("%Y-%m-%dT%H:%M:%S%z"),
                'timeZone': DEFAULT_TIMEZONE,
            },
            'end': {
                'dateTime': self.scheduled_end.strftime("%Y-%m-%dT%H:%M:%S%z"),
                'timeZone': DEFAULT_TIMEZONE,
            },
            'reminders': {
                'useDefault': True,
                'overrides': [],
            },
        }

class GoogleCalendar:
    def __init__(self, context, file_names):
        self.creds_path, token_file = file_names
        self.context = context
        print(self.creds_path)
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

    def get_events(self, calendar_id='primary'):
        start = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0)
        start = (start - timedelta(days=1))
        end = (start + timedelta(days=7))
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
            start = parser.parse(estart.get('dateTime', estart.get(
                    'date'))).replace(tzinfo=pytz.FixedOffset(330))
            end = parser.parse(
                eend.get('dateTime', estart.get('date'))).replace(tzinfo=pytz.FixedOffset(330))
            recurring = True if event.get('recurringEventId', None) else False
            if recurring and not start.date() == date.today():
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
            )

    def create_event(self, event: GoogleCalendarData, calendar_id):
        assert not event.id
        cal_event = event.to_google_event()
        event_dict = self.service.events().insert(calendarId=calendar_id,
                                           body=cal_event).execute()
        event.id = event_dict['id']
        return event

    def update_event(self, event: GoogleCalendarData, calendar_id):
        cal_event = event.to_google_event()
        self.service.events().update(calendarId=calendar_id,
                                     eventId=event.id, body=cal_event).execute()
        return event

    def list_calendars(self):
        lst = self.service.calendarList().list().execute()
        for l_e in lst['items']:
            print(l_e['id'], l_e['summary'], l_e['timeZone'])

    def get_current_events(self, calendar_id=None):
        summary_dict = defaultdict(list)
        for event in self.get_events(calendar_id=calendar_id):
            start, end, summary, link = event
            summary_dict[summary].append((start, end, link))
        for summary, timing, merged in sorted(merge(summary_dict),
                                      key=lambda u: u[1][0]):
            start, end, link = timing
            yield summary, start, end, link, self.context, merged

    @property
    def token(self):
        return f'token-{self.context}.pickle'


def merge(summaries):
    for k, dates in summaries.items():
        if len(dates) > 1:
            dates = [d for d in dates if d[0].date() == datetime.now().date()]
            if dates:
                yield k, dates[0], True
        else:
            yield k, dates[0], False


