from notion.block import TodoBlock, TextBlock, SubheaderBlock, DividerBlock, \
    BulletedListBlock
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


def update_calendar(data):
    url = CONFIG["NOTION_CALENDAR_URL"]
    block = client.get_block(url)
    tt = lambda _u: f'0{_u}' if _u < 10 else f'{_u}'
    lines = "**Schedule for the day**\n"
    lines += ("-" * (len(lines) - 1) + '\n')
    for d in data:
        dts, dte, txt, link = d
        text = f"{tt(dts.hour)}:{tt(dts.minute)} - {tt(dts.hour)}:" \
               f"{tt(dts.minute)} [***{txt}***]({link})\n"
        lines += text
    print(lines)
    block.title = lines


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


def update_project_info_local():
    view_url = CONFIG['NOTION_PROJECT_URL']
    view = client.get_collection_view(view_url)
    assert view is not None and view.collection is not None
    rows = list(_get_rows_by_filter(view, 'Managed', 'local'))
    for row in rows:
        _update_project(client, row)


def _get_rows_by_filter(view, attr, val):
    for row in list(view.collection.get_rows()):
        if str(getattr(row, attr)).lower() == val:
            yield row.id, row


def _update_project(client, row_details):
    row_id, row = row_details
    print("Dealing with ", row_id)
    page = client.get_block(row_id)

    def count_progress(nodes):
        d, t = 0, 0
        for node in nodes:
            print(node)
            if not isinstance(node, TodoBlock):
                continue
            if node.children:
                _d, _t = count_progress(node.children)
            else:
                _t = 1
                _d = 1 if node.checked else 0
            d += _d
            t += _t
        return d, t

    d, t = count_progress(page.children)
    print(d, t, row.title)
    row.Done = int(d)
    row.Total = int(t)


def _generate_keys(*weeks):
    actual_keys = set()
    for d in weeks:
        actual_keys |= set([u[0] for u in d])
    return actual_keys


