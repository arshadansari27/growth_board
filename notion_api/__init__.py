import pytz
from dateutil import parser
from notion.client import NotionClient
from notion.collection import NotionDate

from config import CONFIG
from integration import DB
from integration.calendar_google_api import GoogleCalendarData

TOKEN = CONFIG["NOTION_TOKEN"]


class NotionDB(DB):
    def __init__(self, view_url, lazy=False):
        client = NotionClient(token_v2=TOKEN)
        self.view = client.get_collection_view(view_url)
        assert self.view is not None and self.view.collection is not None
        self.rows = {
            r.title: r
            for r in self.view.collection.get_rows()
        }
        self.client= client
        print('\n'.join(self.rows.keys()))

    def find_one_by(self, field, query):
        if field == 'title':
            return self.rows.get(query)
        for v in self.rows.values():
            if (
                isinstance(getattr(v, field), NotionDate)
                and getattr(v, field).start == query
            ) or getattr(v, field) == query:
                return v
        return None

    def remove_all(self):
        for row in self.rows.values():
            row.remove()

    def get_all(self):
        return list(self.rows.values())

    def get_or_create(self, title):
        if not title in self.rows:
            row = self.view.collection.add_row()
            row.title = title
            self.rows[title] = row
        else:
            row = self.rows[title]
        return row

    def create(self, data):
        _data = {u: v for u, v in data.items()}
        title = _data['title']
        del _data['title']
        row = self.get_or_create(title)
        for k, v in data.items():
            setattr(row, k, v)

    def update(self, data):
        title = data['title']
        del data['title']
        row = self.get_or_create(title)
        for k, v in data.items():
            setattr(row, k, v)

    def remove(self, title):
        row = self.get_or_create(title)
        row.remove()


class NotionCalendarDB(NotionDB):
    FIELDS = ['title', 'schedule', 'link']

    def create(self, cal_data: GoogleCalendarData):
        super(NotionCalendarDB, self).create(self._convert(cal_data))

    def update(self, cal_data: GoogleCalendarData):
        super(NotionCalendarDB, self).update(self._convert(cal_data))

    def _convert(self, cal_data: GoogleCalendarData):
        print('[*]', cal_data)
        return {
            'title': cal_data.name,
            'link': cal_data.link,
            'context': cal_data.context,
            'schedule': NotionDate(
                    start=parser.parse(cal_data.scheduled_start),
                    end=parser.parse(cal_data.scheduled_end),
                    timezone=pytz.FixedOffset(330)
            )
        }


def update_rescue_time(data):
    db = NotionDB(CONFIG["NOTION_RESCUETIME_URL"])
    date = sorted(data.keys())[-1]
    week = dict(data[date])
    actual_keys = week.keys()
    db.remove_all()
    for key in actual_keys:
        row = db.get_or_create(key)
        row.Week4 = round(week.get(key, 0), 2)


