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
      begin, until = create_date(date_today)
      url = get_url(begin, until)
      print(url)
      data = requests.get(url, auth=auth)
      data = data.json()['data']
      data = dict([u for u in [to_proect(u) for u in data] if (u[0][0] and u[0][
          1])])
      return data

def to_proect(dict_data):
     project = dict_data['title']['project']
     client = dict_data['title']['client']
     color = dict_data['title']['hex_color']
     time = dict_data['time']
     return (project, client), time / (3600 * 1000)


def get_weeks_of_data(date_today: datetime, weeks: int=4):
    project_by_date  = {}
    for td in range(weeks):
        dt = date_today - timedelta(days=(td * 7))
        projects = get_data(dt)
        project_by_date[dt.strftime(_FORMAT)] = projects
    return project_by_date


if __name__ == '__main__':
      data = get_weeks_of_data(datetime(2020, 3, 15))
      toggle_view_url = CONFIG['NOTION_TOGGL_URL']
      update_toggl(data, toggle_view_url)
