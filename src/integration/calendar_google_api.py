import os
import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytz
from dateutil import parser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import CONFIG
from integration import DB

PERSONAL = 'Personal'
OFFICE = 'Office'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDS_PATH_OFFICE =  CONFIG["GOOGLE_CREDS_OFFICE_PATH"]
CREDS_PATH_PERSONAL = CONFIG["GOOGLE_CREDS_PERSONAL_PATH"]



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
    def __init__(self, context, creds_path, db: DB):
        self.creds_path = creds_path
        self.context = context
        self.db = db
        token_file = self.token
        creds = None
        if os.path.exists(self.token):
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
        if clean:
            self.db.remove_all()
        for start, end, summary, link in self.get_events():
            data = GoogleCalendarData(summary, str(start), str(end),
                                      self.context, 'confirmed', link)
            self.db.create(data)

    @property
    def token(self):
        return f'token-{self.context}.pickle'

    @staticmethod
    def get_calendar(context):
        from integration.notion_api import NotionCalendarDB
        if context == OFFICE:
            return GoogleCalendar(OFFICE, CREDS_PATH_OFFICE, NotionCalendarDB(
                    CONFIG["NOTION_CALENDAR_URL"]))
        elif context == PERSONAL:
            return GoogleCalendar(PERSONAL, CREDS_PATH_PERSONAL, NotionCalendarDB(
                    CONFIG["NOTION_CALENDAR_URL"]))
        raise NotImplementedError


def update_calendar():
    calendar = GoogleCalendar.get_calendar(PERSONAL)
    calendar.update_events()
    calendar = GoogleCalendar.get_calendar(OFFICE)
    calendar.update_events(clean=False)


if __name__ == '__main__':
    update_calendar()

