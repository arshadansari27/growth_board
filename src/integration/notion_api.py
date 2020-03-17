from notion.client import NotionClient
from notion.collection import NotionDate

from config import CONFIG

TOKEN = CONFIG["NOTION_TOKEN"]


client = NotionClient(token_v2=TOKEN)


def update_jira(issues, context, view_url):
    view = client.get_collection_view(view_url)
    assert view is not None and view.collection is not None
    rows = view.collection.get_rows()
    existing = {r.title: r for r in rows}
    print('\n'.join(existing))
    count = len(issues)
    print("Created", len(existing), 'and todo', count)
    all_components = set()
    all_status = set()
    for issue in issues:
        created = NotionDate(issue['created'])
        updated = NotionDate(issue['updated'])
        row = existing.get(issue['key'])
        creating = False
        if not row:
            row = view.collection.add_row()
            row.title = issue['key']
            creating = True
        elif row.updated and row.updated.start.replace(tzinfo=None) >= updated.start.replace(tzinfo=None):
            print("Skipping issue as it was not updated:", issue['title'])
            continue
        print("Creating" if creating else 'Updating', '->',row.title)
        row.created = created
        row.updated = updated
        row.link = issue['link']
        row.type = issue['type']
        row.subtask = issue['subtask']
        row.components = issue['components']
        all_components |= set(issue['components'])
        row.description = issue['description']
        row.summary = issue['title']
        row.status = issue['status']
        all_status.add(issue['status'])
        row.parent = issue['parent']
        row.project_key = issue['project_key']
        row.project = issue['project']
        row.context = context
    print(all_components)
    print(all_status)

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


