from collections import defaultdict
from datetime import datetime, timedelta, date

from config import CONFIG, NOTION_HABIT_ROUTINE_URL, NOTION_TRACKING_DAILY_URL, \
    NOTION_HOTSPOTS_URL
from notion_api import NotionDB


def update_all_time_aggregates():
    today = datetime.now().date()
    tracker_db = NotionDB(CONFIG[NOTION_TRACKING_DAILY_URL])
    habits_db = NotionDB(CONFIG[NOTION_HABIT_ROUTINE_URL])
    hotspots_db = NotionDB(CONFIG[NOTION_HOTSPOTS_URL])
    hotspots_keys = {u.Tracker: u.title for u in hotspots_db.rows.values()}
    habits_keys = set(habits_db.rows.keys())
    keys = habits_keys.union(set(hotspots_keys.keys()))
    current_dict = defaultdict(list)
    previous_dict = defaultdict(list)
    print("Begin Tracking...")
    count = 0
    for row in tracker_db.rows.values():
        count += 1
        print(count)
        week_id = row.Week[0].id
        week = tracker_db.client.get_block(week_id)
        current = _is_current_week(today, week)
        previous = _is_previous_week(today, week)
        for k in keys:
            col_value = getattr(row, k, None)
            if not col_value:
                v = 0
            elif col_value == True:
                v = 1
            else:
                v = col_value
            if current:
                current_dict[k].append(v)
            if previous:
                previous_dict[k].append(v)
    _update_hotspots(hotspots_db, hotspots_keys, current_dict, previous_dict)
    #_update_habits(habits_db, habits_keys, current_dict, previous_dict)


def _is_current_week(today: date, week):
    return week.Week.start < today < week.Week.end


def _is_previous_week(today: date, week):
    return today > week.Week.end and (
            today < (datetime.now() + timedelta(days=8)).date())


def _update_hotspots(hotspots_db, keys, current_hotspots, previous_hotspots):
    _update_time_aggregates(hotspots_db, 'TimeAggCurr', keys, current_hotspots,
                            'sum')
    _update_time_aggregates(hotspots_db, 'TimeAggPrev', keys, previous_hotspots,
                            'sum')


def _update_habits(habits_db, keys, current_habits, previous_habits):
    _update_time_aggregates(habits_db, 'Status', keys, current_habits, 'avg')
    _update_time_aggregates(habits_db, 'StatusPrev', keys, previous_habits,
                            'avg')


def _update_time_aggregates(db, agg_key, keys, value_dict, method):
    for k in keys:
        if isinstance(keys, dict):
            row = db.get_or_create(keys[k])
        else:
            row = db.get_or_create(k)
        if method == 'sum':
            value = sum(value_dict[k])
        elif method == 'avg':
            value = sum(value_dict[k]) / len(value_dict[k])
        else:
            value = 0
        setattr(row, agg_key, value)
        print(method, row.title, agg_key, value, value_dict[k])


if __name__ == '__main__':
    update_all_time_aggregates()