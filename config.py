import os
from urllib.parse import urlsplit

import requests
from notion.client import NotionClient


def set_from_enviorn(config, val):
    config[val] = os.environ.get(val, '').replace('"', '')
    if not config[val]:
        print(f"Configuration for {val} not set")


def set_from_value(config, key, value):
    config[key] = value


def get_from_url(value: str):
    try:
        i = value.index(']')
        j = value.index('(')
    except ValueError:
        i = 0
        j = 0
    if value.startswith('[') and value.endswith(')') and i > 0 and j == (i+1):
        return value[1:i]
    return value


def save_file(file_url, as_binary=False):
    file_name = urlsplit(file_url).path.split('/')[-1]
    if not os.path.exists(file_name):
        print("[*] Saving file to local", file_name)
        with open(file_name, 'wb' if as_binary else 'w') as outfile:
            response = requests.get(file_url)
            if not as_binary:
                outfile.write(response.text)
            else:
                for chunk in response.iter_content(1024):
                    outfile.write(chunk)
    return file_name


CONFIG = {}
NOTION_TOKEN = "NOTION_TOKEN"
NOTION_CONFIG = "NOTION_CONFIG"
GOOGLE_CREDS_PERSONAL = "Google Calendar Personal Credentials File"
GOOGLE_CREDS_OFFICE = "Google Calendar Office Credentials File"

set_from_enviorn(CONFIG, NOTION_TOKEN)
set_from_enviorn(CONFIG, NOTION_CONFIG)


def setup_conf():
    client = NotionClient(token_v2=CONFIG[NOTION_TOKEN])
    config_view = client.get_collection_view(CONFIG[NOTION_CONFIG])
    for row in config_view.collection.get_rows():
        if row.title in {GOOGLE_CREDS_OFFICE, GOOGLE_CREDS_PERSONAL}:
            creds_file_url = [u for u in row.Files if 'credentials' in u][0]
            cres_file_name = save_file(creds_file_url)
            token_file_url = [u for u in row.Files if 'token' in u][0]
            token_file_name = save_file(token_file_url, True)
            CONFIG[row.title] = (cres_file_name, token_file_name)
            continue
        u = get_from_url(row.Value)
        set_from_value(CONFIG, row.title, u)


NOTION_GOALS_URL=""
NOTION_PROJECT_URL="Project"
NOTION_TASKS_URL="Tasks"
NOTION_BOOK_LIBRARY_URL="Books"
NOTION_VIDEO_LIBRARY_URL='Videos'
NOTION_TRACKING_DAILY_URL="Daily Tracking"
NOTION_TRACKING_WEEKLY_URL="Weekly Tracking"
NOTION_HABIT_ROUTINE_URL="Habits"
NOTION_HOTSPOTS_URL="Hotspots"
NOTION_TRACKABLE_THINGS_URL="Trackable Things"
RESCUETIME_URL="Rescue Time Api"
TOGGL_URL="Toggl Api"
TOGGL_KEY="Toggl Key"
JIRA_STOCKY_URL="Jira Stocko Api"
JIRA_STOCKY_USER="Jira Stocko User"
JIRA_STOCKY_KEY="Jira Stocko Key"
JIRA_PERSONAL_URL="Jira Personal Api"
JIRA_PERSONAL_USER="Jira Personal User"
JIRA_PERSONAL_KEY="Jira Personal Key"
AIRTABLE_API_KEY="Airtable Key"
NOTION_QA_HIRING_URL = "QA Hiring Board"
NOTION_BE_HIRING_URL = "BE Hiring Board"

if CONFIG.get(NOTION_TOKEN, False) and CONFIG.get(NOTION_CONFIG, False):
    setup_conf()