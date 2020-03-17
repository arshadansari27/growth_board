from notion.block import TodoBlock, TextBlock, SubheaderBlock, DividerBlock
from notion.client import NotionClient
from notion.collection import NotionDate

from config import CONFIG

TOKEN = CONFIG["NOTION_TOKEN"]


client = NotionClient(token_v2=TOKEN)
def get_client():
    return client

def update_project_info(cards):
    view_url = CONFIG['NOTION_PROJECT_URL']
    view = client.get_collection_view(view_url)
    assert view is not None and view.collection is not None
    rows = list(view.collection.get_rows())
    existing = {r.title: r for r in rows}
    for card in cards.values():
        if card.project in existing:
            row = existing[card.project]
        else:
            row = view.collection.add_row()
            row.title = card.project
        row.Done = card.done
        row.Total = card.total
        row.SubDone = card.sub_done
        row.SubTotal = card.sub_total
        row.Type = card.type
        page = client.get_block(row.id)
        for c in page.children:
            c.remove(permanently=True)
        page.children.add_new(SubheaderBlock, title="Current")
        for text in card.on_going:
            page.children.add_new(TodoBlock, title=text)
        page.children.add_new(DividerBlock)
        page.children.add_new(SubheaderBlock, title="Coming Up Next")
        for text in card.up_next:
            page.children.add_new(TodoBlock, title=text)

'''
def update_jira(issues, context, view_url):
    view = client.get_collection_view(view_url)
    assert view is not None and view.collection is not None
    rows = view.collection.get_rows()
    existing = {r.title: r for r in rows}
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
'''

def update_toggl(data):
    view_url = CONFIG['NOTION_TOGGL_URL']
    view = client.get_collection_view(view_url)
    assert view is not None and view.collection is not None
    date = sorted(data.keys())[-1]
    week = data[date]
    actual_keys = week.keys()
    rows = view.collection.get_rows()
    existing = {r.title: r for r in rows}
    for _client in actual_keys:
        if not _client:
            print(_client, 'skipping...')
            continue
        print(_client, 'beginning...')
        existing_client = existing.get(_client)
        print('\t', existing_client)
        if not existing_client:
            row = view.collection.add_row()
            row.title = _client
            print('\tCreating')
        else:
            row = existing_client
            print('\tUpdating')
        row.Toggl = round(week.get(_client, 0), 2)
        print(_client, 'done')
    print('Done...')


def update_rescue_time(data):
    view_url = CONFIG["NOTION_RESCUETIME_URL"]
    view = client.get_collection_view(view_url)
    assert view is not None
    date = sorted(data.keys())[-1]
    week = dict(data[date])
    actual_keys = week.keys()
    rows = view.collection.get_rows()
    for row in rows:
        row.remove()
    for key in actual_keys:
        row = view.collection.add_row()
        row.title = key
        row.Week4 = round(week.get(key, 0), 2)
        print(key, 'done')
    print('Done...')


def _generate_keys(*weeks):
    actual_keys = set()
    for d in weeks:
        actual_keys |= set([u[0] for u in d])
    return actual_keys


