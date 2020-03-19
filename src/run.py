from integration.google_calendar_to_notion import update_notion_calendar
from integration.jira_api import update_notion_projects
from integration.notion_api import update_project_info_local
from integration.rescuetime_to_notion import update_apps
from integration.toggle_to_notion import update_hotspots

if __name__ == '__main__':
    update_notion_calendar()
    update_project_info_local()
    update_notion_projects()
    update_hotspots()
    update_apps()

