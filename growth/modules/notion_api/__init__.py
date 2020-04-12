from typing import Dict, Any, List, Tuple

import requests
from notion.client import NotionClient
from notion.collection import NotionDate

from growth.config import CONFIG


class NotionDB:
    def __init__(self, view_url, lazy=False, token=False):
        if not token:
            token = CONFIG["NOTION_TOKEN"]
        client = NotionClient(token_v2=token)
        self.view = client.get_collection_view(view_url)
        assert self.view is not None and self.view.collection is not None
        if not lazy:
            self._rows = {
                r.title: r
                for r in self.view.collection.get_rows()
            }
        else:
            self._rows = {}
        self.client = client

    @property
    def rows(self) -> Dict[str, Any]:
        if not self._rows:
            self._rows = {
                r.title: r
                for r in self.view.collection.get_rows()
            }
        return self._rows

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

    def get(self, title):
        return self.rows.get(title, None)

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

    def upload_file(self, title, field, content_type, file_name, file_object):
        response = self.client.post('/api/v3/getUploadFileUrl', data={
            "bucket": "secure",
            "name": file_name,
            "contentType": content_type
        })
        resp_data = response.json()
        # get_url = resp_data['signedGetUrl']
        url = resp_data['url']
        put_url = resp_data['signedPutUrl']
        header = {"Origin": "localhost", "Content-type": content_type}
        requests.put(put_url, data=file_object, headers=header)
        row = self.get_or_create(title)
        field_values = getattr(row, field, [])
        field_values.append(url)
        print(row.title, field_values)
        setattr(row, field, field_values)

    def remove(self, title):
        row = self.get_or_create(title)
        row.remove()


def update_rescue_time(data):
    db = NotionDB(CONFIG["NOTION_RESCUETIME_URL"])
    date = sorted(data.keys())[-1]
    week = dict(data[date])
    actual_keys = week.keys()
    db.remove_all()
    for key in actual_keys:
        row = db.get_or_create(key)
        row.Week4 = round(week.get(key, 0), 2)


def create_filter(property, value, operator='contains'):
    return {
        'filter': {
            'value': {
                'type': 'exact',
                'value': value
            },
            'operator': operator
        },
        'property': property
    }


def create_filter_list(filter_tuples: List[Tuple[str, Any, str]]):
    return {
        'filter': {
            'filters': [create_filter(*filter_tuple) for filter_tuple in
                        filter_tuples],
            'operator': 'and'
        }
    }
