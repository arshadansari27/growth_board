import time

from integration.calendar_google_api import update_calendar
from integration.jira_api import update_notion_jira_tasks
from integration.rescuetime_to_notion import update_apps
from integration.toggle_to_notion import update_hotspots


def run_quicker():
    update_calendar()

def run_in_long_interval():
    update_notion_jira_tasks()
    update_hotspots()
    update_apps()


def run_all():
    count = 0
    while True:
        print("RUN QUICKLY")
        run_quicker()
        if count % 10 is 0:
            print("RUN IN LONG INTERVAL")
            run_in_long_interval()
        count += 1
        time.sleep(10 * 60)


if __name__ == '__main__':
    run_all()
