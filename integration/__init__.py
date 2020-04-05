from abc import ABC, abstractmethod
from datetime import datetime, timedelta

_FORMAT = "%Y-%m-%d"


def create_date(date_today: datetime):
    week_day = date_today.weekday()
    start_week = date_today - timedelta(days=week_day)
    return start_week.strftime(_FORMAT), date_today.strftime(_FORMAT)

