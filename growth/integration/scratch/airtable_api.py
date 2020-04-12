from dataclasses import dataclass
from airtable import airtable
from growth.config import CONFIG
from growth.integration.calendar_google_api import GoogleCalendarData

API_KEY=CONFIG.get('AIRTABLE_API_KEY')


class GoogleCalendarAirtableDB:
    BASE_ID = 'appu85Hp5jCkZMC9h'
    TABLE_NAME = 'Google Calendar'
    FIELD_MAPPING = {
        'Name': 'name',
        'Schedule Start': 'scheduled_start',
        'Schedule End': 'scheduled_end',
        'Context': 'context',
        'Status': 'status',
    }

    def __init__(self, api_key):
        self.api_key = api_key
        self.at = airtable.Airtable(self.BASE_ID, API_KEY)

    def _to_row(self, record):
        record_id = record['id']
        data = {}
        fields = record['fields']
        for k, v in fields.items():
            data[self.FIELD_MAPPING[k]] = v
        return GoogleCalendarData(record_id, **data)

    def _to_record(self, google_calender_data: GoogleCalendarData):
        id = google_calender_data.id
        data = {
            'Name': google_calender_data.name,
            'Schedule Start': google_calender_data.scheduled_start,
            'Schedule End': google_calender_data.scheduled_end,
            'Context': google_calender_data.context,
            'Status': google_calender_data.status,
        }
        return id, data

    def get(self, id: str):
        record = self.at.get(self.TABLE_NAME, record_id=id)
        return self._to_row(record)

    def get_or_create(self, name: str):
        records = self.at.iterate(self.TABLE_NAME)
        for record in records:
            data = self._to_row(record)
            if data.name == name:
                return data
        data = GoogleCalendarData(None, name)
        return self.create(data)

    def update(self, data: GoogleCalendarData):
        rec_id, record = self._to_record(data)
        self.at.update(self.TABLE_NAME, rec_id, record)

    def create(self, data: GoogleCalendarData):
        assert data.id is None
        _, record = self._to_record(data)
        created_record = self.at.create(self.TABLE_NAME, record)
        return self._to_row(created_record)

    def all(self):
        return [self._to_row(u) for u in self.at.get(self.TABLE_NAME)[
            'records']]


google_calendar_airflow = GoogleCalendarAirtableDB(API_KEY)

