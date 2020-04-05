from apscheduler.schedulers.blocking import BlockingScheduler

from notion_api.calendar_updater import update_calendar_times
from notion_api.time_agg_updater import update_all_time_aggregates
from notion_api.hotspot_updater import update_daily_hotspots
from notion_api.task_updater import update_tasks


sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=23)
def hotspot_updater():
    print('Runs every 25 mins for daily updates')
    update_daily_hotspots()
    update_all_time_aggregates()


@sched.scheduled_job('interval', minutes=4)
def log_updater():
    print('Runs every 4 mins for calendar update')
    update_calendar_times()


@sched.scheduled_job('interval', minutes=31)
def task_updater():
    print('Runs every 31 mins for task updates')
    update_tasks()


sched.start()