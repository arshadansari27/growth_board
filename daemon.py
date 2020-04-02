from apscheduler.schedulers.blocking import BlockingScheduler

from notion_api.time_agg_updater import update_all_time_aggregates
from notion_api.hotspot_updater import update_daily_hotspots
from notion_api.task_updater import update_tasks


sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=25)
def hotspot_updater():
    update_daily_hotspots()
    update_all_time_aggregates()


@sched.scheduled_job('interval', minutes=7)
def log_updater():
    print('This job is runs every minute to let you know that things are '
          'actually running.')


@sched.scheduled_job('interval', hours=4)
def task_updater():
    update_tasks()


sched.start()