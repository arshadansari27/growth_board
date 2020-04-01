import os

from notion.client import NotionClient


def set_from_enviorn(config, val):
    config[val] = os.environ[val].replace('"', '')


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


CONFIG = {}
NOTION_TOKEN = "NOTION_TOKEN"
NOTION_CONFIG = "NOTION_CONFIG"


set_from_enviorn(CONFIG, NOTION_TOKEN)
set_from_enviorn(CONFIG, NOTION_CONFIG)

client = NotionClient(token_v2=CONFIG[NOTION_TOKEN])
config_view = client.get_collection_view(CONFIG[NOTION_CONFIG])
for row in config_view.collection.get_rows():
    u = get_from_url(row.Value)
    set_from_value(CONFIG, row.title, u)


NOTION_GOALS_URL=""
NOTION_PROJECT_URL="Project"
NOTION_TASKS_URL="Tasks"
NOTION_BOOK_LIBRARY_URL="Books"
NOTION_VIDEO_LIBRARY_URL='Videos'
NOTION_TRACKING_DAILY_URL="Daily Tracking"
NOTION_HABIT_ROUTINE_URL="Habits"
NOTION_HOTSPOTS_URL="Hotspots"
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
