import json
import os
from multiprocessing.pool import ThreadPool
from typing import Dict, Any, List, Tuple

import requests
from notion.client import NotionClient
from notion.collection import NotionDate
from pymongo import MongoClient

from growth.config import CONFIG, NOTION_TOKEN


class DatabaseEngine:

    def __init__(self, collection, db_url, db_name, **kwargs):
        self._collection = collection
        client = MongoClient(db_url)
        self.db = client.get_database(db_name)

    @property
    def collection(self):
        return getattr(self.db, self.collection)

    def is_empty(self) -> bool:
        return self.collection.find({}).count() > 0

    def get_id_by_title(self, title) -> str:
        doc = self.collection.find_one({'_id': title})
        if not doc:
            return None
        return doc['id']

    def save_id_for_title(self, title, uid) -> None:
        self.collection.update({'_id': title}, {'$set': {'id': uid}}, upsert=True)


class NotionDBv2:
    def __init__(self, view_url, database_engine: DatabaseEngine):
        token = CONFIG[NOTION_TOKEN]
        self.database_engine = database_engine
        self.client = NotionClient(token_v2=token)
        self.view = self.client.get_collection_view(view_url)
        rows = self.view.collection.get_rows()
        self.block_ids = rows._block_ids
        self.get_block = rows._get_block
        self.rows = {}
        self.ran_setup = False
        if self.database_engine.is_empty():
            self._setup_rows()
        else:
            print("[*] DB Loaded")

    def get(self, title):
        row = self.rows.get(title, None)
        if not row:
            uid = self.database_engine.get_id_by_title(title)
            if uid:
                row = self.get_block(uid)
                self.rows[title] = row
        return self.rows.get(title)

    def get_or_create(self, title):
        row = self.get(title)
        if self.database_engine.is_empty() and not self.ran_setup:
            raise Exception("How was this not setup earlier?")
        if not row:
            row = self.view.collection.add_row()
            row.title = title
            self.rows[title] = row
            self.database_engine.save_id_for_title(title, row.id)
        return self.rows[title]

    def _setup_rows(self):
        print("SETTING UP")
        done_block_ids = set()
        that = self

        def _get_block(_id):
            done_block_ids.add(_id)
            percent = round((float(len(done_block_ids)) / len(that.block_ids)) * 100, 2)
            row = self.get_block(_id)
            print(f"[{percent}%%] Got {row.title} for id = {_id}")
            return row

        with ThreadPool(processes=10) as pool:
            full_rows = pool.map(_get_block, [block_id for block_id in self.block_ids])
            for row in full_rows:
                if row.title in self.rows:
                    continue
                self.rows[row.title] = row
                self.database_engine.save_id_for_title(row.title, row.id)
        self.ran_setup = True


class NotionDB:
    def __init__(self, view_url, lazy=False, token=False):
        if not token:
            token = CONFIG["NOTION_TOKEN"]
        client = NotionClient(token_v2=token)
        self.view = client.get_collection_view(view_url)
        assert self.view is not None and self.view.collection is not None
        results = self.view.collection.get_rows()
        print("FOUND ROWS", results._block_ids)
        if not lazy:
            print("[NotionDB] Getting data from collection")
            self._rows = {
                r.title: r
                for r in results
            }
            print("[NotionDB] Done getting data from collection")
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

    def upload_file(self, content_type, file_name, file_object):
        response = self.client.post('/api/v3/getUploadFileUrl', data={
            "bucket": "secure",
            "name": file_name,
            "contentType": content_type
        })
        resp_data = response.json()
        get_url = resp_data['signedGetUrl']
        url = resp_data['url']
        put_url = resp_data['signedPutUrl']
        header = {"Origin": "localhost", "Content-type": content_type}
        response = requests.put(put_url, data=file_object, headers=header)
        response.raise_for_status()
        print('FILE GET', get_url)
        print('FILE', url)
        return url

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
