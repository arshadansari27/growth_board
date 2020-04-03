import os
import pickle
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

        today = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0)
        tomorrow = (today + timedelta(days=1))
        time_min = today.isoformat() + 'Z'
        time_max = tomorrow.isoformat() + 'Z'
        events_result = self.service.events().list(
                calendarId='primary', timeMin=time_min,
                timeMax=time_max, singleEvents=True).execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
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

    def update_events(self, clean=True):
        for start, end, summary, link in self.get_events():
            data = GoogleCalendarData(summary, str(start), str(end),
                                      self.context, 'confirmed', link)
            print(data)

    @property
    def token(self):
        return f'token-{self.context}.pickle'



