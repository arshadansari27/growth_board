from collections import defaultdict
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth

from config import CONFIG
from integration import create_date, _FORMAT
from integration.notion_api import update_toggl

URL = CONFIG["TOGGL_URL"]
api_key = CONFIG['TOGGL_KEY']


def get_url(since, until):
    return URL + f"&since={since}&until={until}"


def get_data(date_today: datetime):
    auth = HTTPBasicAuth(api_key, 'api_token')
    today = date_today.strftime(_FORMAT)
    url = get_url(today, today)
    data = requests.get(url, auth=auth)
    data = data.json()['data']
    data = [u for u in [to_proect(u) for u in data] if u[0]]
    return aggregate_data(data)


def to_proect(dict_data):
     client = dict_data['title']['client']
     time = dict_data['time']
     return client, round(time / (3600 * 1000), 2)


def aggregate_data(data):
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


def update_hotspots():
    data = get_data(datetime(2020, 3, 15))
    print(data)
    #update_toggl(data)


if __name__ == '__main__':
    update_hotspots()