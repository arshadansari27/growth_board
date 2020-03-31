from datetime import datetime, timedelta

import pytz
import requests
from requests.auth import HTTPBasicAuth

from config import CONFIG, TOGGL_URL, NOTION_TRACKING_DAILY_URL, TOGGL_KEY
from notion_api import NotionDB

daily_tracking_url = CONFIG[NOTION_TRACKING_DAILY_URL]
toggl_url = CONFIG[TOGGL_URL]
api_key = CONFIG[TOGGL_KEY]


def update_daily_hotspots():
    end_date = datetime.now(tz=pytz.FixedOffset(330))
    start_date = end_date - timedelta(days=7)
    daily_tracking_db = NotionDB(daily_tracking_url)
    while start_date <= end_date:
        set_final = False if start_date >= end_date else True
        st = start_date.date()
        row = daily_tracking_db.find_one_by('Date', st)
        if row and not row.Final:
            print('Updating:', row.title, st)
            data = get_data(st)
            for k, v in data.items():
                setattr(row, k, v)
            if set_final:
                row.Final = True
        else:
            print("Skipping", st)
        start_date += timedelta(days=1)

def get_data(today):
    def _client_data(dict_data):
        client = dict_data['title']['client']
        time = dict_data['time']
        return client, round(time / (3600 * 1000), 2)

    auth = HTTPBasicAuth(api_key, 'api_token')
    url = toggl_url + f"&since={today}&until={today}"
    data = requests.get(url, auth=auth)
    data = data.json()['data']
    data = [u for u in [_client_data(u) for u in data] if u[0]]
    by_client = {
        'Fun': [],
        'Career':[],
        'Relationship': [],
        'Mind': [],
        'Deen': [],
        'Body': [],
        'Chores':[],
    }
    for c, t in data:
        by_client[c].append(t)
    return {c: sum(t) for c, t in by_client.items()}


if __name__ == '__main__':
    update_daily_hotspots()