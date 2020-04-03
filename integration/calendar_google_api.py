import os
import pickle
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytz
from dateutil import parser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

PERSONAL = 'Personal'
OFFICE = 'Office'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



@dataclass
class GoogleCalendarData:
    name: str
    scheduled_start: str = None
    scheduled_end: str = None
    context:str = None
    status: str = None
    link: str = None

    def __repr__(self):
        return f"[{self.context}]: {self.name} ({self.status})"

    def to_dict(self):
        return {
            'name': self.name,
            'scheduled_start': self.scheduled_start,
            'scheduled_end': self.scheduled_end,
            'context': self.context,
            'status': self.status,
            'link': self.link,
        }

class GoogleCalendar:
    def __init__(self, context, file_names):
        self.creds_path, token_file = file_names
        self.context = context
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

    def get_events(self):
        start = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0)
        start = (start - timedelta(days=1))
        end = (start + timedelta(days=7))
        time_min = start.isoformat() + 'Z'
        time_max = end.isoformat() + 'Z'
        events_result = self.service.events().list(
                calendarId='primary', timeMin=time_min,
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
            summary = event['summary']
            link = event['htmlLink']
            yield (
                start,
                end,
                summary,
                link
            )

    def get_current_events(self):
        summary_dict = defaultdict(list)
        for event in self.get_events():
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


