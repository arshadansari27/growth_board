from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=23)
def hotspot_updater():
    print('Runs every 25 mins for daily updates')


@sched.scheduled_job('interval', minutes=4)
def log_updater():
    print('Runs every 4 mins for calendar update')


@sched.scheduled_job('interval', minutes=31)
def task_updater():
    print('Runs every 31 mins for task updates')


sched.start()