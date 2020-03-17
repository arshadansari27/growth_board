import json
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil import parser

import requests

from config import CONFIG
from integration import create_date, _FORMAT
from integration.notion_api import update_rescue_time

URL = CONFIG['RESCUETIME_URL']
KEYS =['Date', 'Time Spent (seconds)', 'Number of People', 'Activity',
         'Category', 'Productivity']
[DATE, TIME_SPENT, PEOPLE, ACTIVITY, CATEGORY, PRODUCTIVITY] = KEYS


def get_url(begin, end):
    return URL + f"&resolution_time=week&restrict_begin={begin}" \
                 f"&restrict_end={end}&format=json"


def get_data(date_today: datetime):
    begin, end = create_date(date_today)
    data = requests.get(get_url(begin, end))
    data = data.json()
    headers = data['row_headers']
    rows = data['rows']
    return map(to_date, [dict(zip(headers, row)) for row in rows])


def to_date(dict_data):
    dict_data[DATE] = parser.parse(dict_data[DATE])
    return dict_data

def by_activity(dict_data):
    tt = dict_data[TIME_SPENT]
    time_spent = round(tt / 3600, 2)
    activity = dict_data[ACTIVITY]
    category = dict_data[CATEGORY]
    return category, activity, time_spent


def convert_to_dict(list_of_dicts):
    by_date_category = defaultdict(float)
    by_date_activity = defaultdict(float)
    for u in list_of_dicts:
        c, a, t = by_activity(u)
        by_date_category[c] += t
        by_date_activity[a] += t
    return by_date_category, by_date_activity


def get_weeks_of_data(date_today: datetime, weeks: int=4):
    category_by_date = {}
    activity_by_date = {}
    for td in range(weeks):
        dt = date_today - timedelta(days=(td * 7))
        categories, activity = convert_to_dict(list(get_data(dt)))
        category_by_date[dt.strftime(_FORMAT)] = sorted(
            [(u, v) for u, v in categories.items()],
            key=lambda x: x[1], reverse=True)[:5]
        activity_by_date[dt.strftime(_FORMAT)] = sorted(
                [(u, v) for u, v in activity.items()],
                key=lambda x: x[1], reverse=True)[:5]
    return category_by_date, activity_by_date

def update_apps():
    _, activity = get_weeks_of_data(datetime.now(), 2)
    update_rescue_time(activity)


