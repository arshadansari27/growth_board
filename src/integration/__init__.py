from abc import ABC, abstractmethod
from datetime import datetime, timedelta

_FORMAT = "%Y-%m-%d"


def create_date(date_today: datetime):
    week_day = date_today.weekday()
    start_week = date_today - timedelta(days=week_day)
    return start_week.strftime(_FORMAT), date_today.strftime(_FORMAT)


class DB(ABC):

    @abstractmethod
    def remove_all(self):
        pass

    @abstractmethod
    def get_or_create(self, name: str):
        pass

    @abstractmethod
    def update(self, data):
        pass

    @abstractmethod
    def remove(self, name: str):
        pass

    @abstractmethod
    def create(self, data):
        pass
