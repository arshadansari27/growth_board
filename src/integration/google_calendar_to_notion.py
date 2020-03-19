from __future__ import print_function
import datetime
import pickle
import os.path
from pathlib import Path

from dateutil import parser
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from integration.notion_api import update_calendar

PERSONAL = 'Personal'
OFFICE = 'Office'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
BASE = Path(__file__).absolute().parent.parent
CREDS_PATH_OFFICE =  BASE / "credentials-stockopedia.json"
CREDS_PATH_PERSONAL = BASE / "credentials-arshadansari27.json"


def get_path(context):
    if context == 'Office':
        return CREDS_PATH_OFFICE
    elif context == 'Personal':
        return CREDS_PATH_PERSONAL
    raise NotImplementedError


def main(context):
    creds = None

    def get_token_file():
        return f'token-{context}.pickle'

    token_file = get_token_file()
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(get_path(context), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    today = datetime.datetime.utcnow().replace(hour=0, minute=0,
                                             second=0,
                                             microsecond=0)
    tomorrow = (today + datetime.timedelta(days=1))
    time_min = today.isoformat() + 'Z'
    time_max = tomorrow.isoformat() + 'Z'
    events_result = service.events().list(
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
                'date'))).replace(tzinfo=None)
        end = parser.parse(eend.get('dateTime', estart.get('date'))).replace(tzinfo=None)
        summary = event['summary']
        link = event['htmlLink']
        yield (
            start,
            end,
            summary,
            link
        )


def merge_data(*data):
    all_d = []
    for d in data:
        all_d.extend([
            (u[0], u[1], u[2], u[3])
            for u in d
        ])
    return sorted(all_d)


def update_notion_calendar():
    d1 = list(main(PERSONAL))
    d2 = list(main(OFFICE))
    data = []
    for u in merge_data(d1, d2):
        data.append((u[0], u[1], u[2], u[3]))
    update_calendar(data)


if __name__ == '__main__':
    update_notion_calendar()
