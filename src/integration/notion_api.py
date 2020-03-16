from notion.client import NotionClient
from notion.collection import NotionDate

TOKEN = "76c45addb4795e4e324231c33610975e4aadf213f43b062bac51316343bfc7001e17053c3c65e87bc4375b9a525f9cd4f544cf9b1dc7b5cadcf534851e03105b4ffed4e936726b948d4d5048c405"


client = NotionClient(token_v2=TOKEN)


def update_projects_and_tasks(data, view_url):
    view = client.get_collection_view(view_url)
    assert view is not None
    rows = view.collection.get_rows()
    existing = {r.title: r for r in rows}
    print("Created", len(existing), 'and todo', len(data))
    count = len(data)
    for task, list, project, status, date_due, date_start, tags in data:
        if date_start and date_due:
            schedule = NotionDate(start=date_start, end=date_due)
        elif date_due:
            schedule = NotionDate(date_due)
        else:
            schedule = None
        row = existing.get(task)
        if row:
            if row.Project == list and row.Context == project and (not tags or
                                                                 row.tags == tags):
                print("Skipping", row.title)
                continue
            else:
                print("Updating Existing", row.title)
        else:
            print("Creating New...", task)
            row = view.collection.add_row()
            row.title = task

        count -= 1
        print("\t\tRemaining", count)
        (row.Project, row.Context, row.Schedule, row.Status, row.tags) = (
            list, project, schedule, status, tags)
        print('\tDone: ', row.title, 'on', schedule, date_due, date_start)
    print('Done...')


def update_toggl(data, view_url):
    view = client.get_collection_view(view_url)
    assert view is not None
    dates = sorted(data.keys())
    weeks = [data[dates[i]] for i in range(4)]
    actual_keys = _generate_keys(*weeks)
    rows = view.collection.get_rows()
    for project, _client in actual_keys:
        if not rows or project not in {r.title for r in rows}:
            row = view.collection.add_row()
            row.title = project
            row.Client = _client
        else:
            row = [r for r in rows if r.title == project][0]
        [rw1, rw2, rw3, rw4] = [round(week.get((project, _client), 0), 2) for
                                week in weeks]
        row.Week1, row.Week2, row.Week3, row.Week4 = rw1, rw2, rw3, rw4
        print(project, _client, 'done')
    print('Done...')


def update_rescue_time(data, view_url):
    view = client.get_collection_view(view_url)
    assert view is not None
    dates = sorted(data.keys())
    weeks = [data[dates[i]] for i in range(4)]
    actual_keys = _generate_keys(*weeks)
    rows = view.collection.get_rows()
    for key in actual_keys:
        if not rows or key not in {r.title for r in rows}:
            row = view.collection.add_row()
            row.title = key
        else:
            row = [r for r in rows if r.title == key][0]
        [rw1, rw2, rw3, rw4] = [round(week.get(key, 0), 2) for week in weeks]
        row.Week1, row.Week2, row.Week3, row.Week4 = rw1, rw2, rw3, rw4
        print(key, 'done')
    print('Done...')


def _generate_keys(*dicts):
    actual_keys = set()
    for d in dicts:
        actual_keys |= set(d.keys())
    return actual_keys


