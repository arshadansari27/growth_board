from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from notion_api.hotspot_updater import update_daily_hotspots
from notion_api.task_updater import update_tasks

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=1)
def hotspot_updater():
    print('This job is run every hour.')
    update_daily_hotspots()


@sched.scheduled_job('interval', minutes=1)
def log_updater():
    print('This job is runs every minute to let you know that things are '
          'actually running.')

@sched.scheduled_job('cron', day_of_week="mon-fri", hour=3)
def task_updater():
    update_tasks()

sched.start()