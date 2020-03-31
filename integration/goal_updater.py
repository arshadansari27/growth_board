from notion.block import CollectionViewBlock

from config import CONFIG
from notion_api import NotionDB

TASK_PROPERTY = '@qm>'
BOOK_PROPERTY = '*fnW'
VIDEO_PROPERTY =  '&r0m'

def update_goals():
    goal_db = NotionDB(CONFIG['NOTION_GOALS_URL'])
    client = goal_db.client
    for goal in goal_db.get_all():
        block = client.get_block(goal.id)
        print(goal.title, len(block.children))
        update_task_list(goal, client)
        update_books_list(goal, client)
        update_videos_list(goal, client)

def update_task_list(goal, client):
    task_url = CONFIG['NOTION_TASKS_URL']
    original_collection_view = client.get_collection_view(task_url)
    block = client.get_block(goal.id)
    tasks_attached = False
    for child in block.children:
        if get_title(child) == 'Tasks':
            tasks_attached = True
    if tasks_attached:
        print('\t', "Attached tasks, so skipping")
        return
    print('\t', "Attached tasks not found, so adding...")
    collection = client.get_collection(original_collection_view.collection.id)
    cvb = block.children.add_new(CollectionViewBlock, collection=collection)
    view = cvb.views.add_new(view_type="board")
    view.set('query2', get_filter(block, TASK_PROPERTY))

def update_books_list(goal, client):
    book_url = CONFIG['NOTION_BOOK_LIBRARY_URL']
    original_collection_view = client.get_collection_view(book_url)
    block = client.get_block(goal.id)
    tasks_attached = False
    for child in block.children:
        if get_title(child) == 'Book Library':
            tasks_attached = True
    if tasks_attached:
        print('\t', "Attached books, so skipping")
        return
    print('\t', "Attached books not found, so adding...")
    collection = client.get_collection(original_collection_view.collection.id)
    cvb = block.children.add_new(CollectionViewBlock, collection=collection)
    view = cvb.views.add_new(view_type="list")
    view.set('query2', get_filter(block, BOOK_PROPERTY))


def update_videos_list(goal, client):
    book_url = CONFIG['NOTION_VIDEO_LIBRARY_URL']
    original_collection_view = client.get_collection_view(book_url)
    block = client.get_block(goal.id)
    tasks_attached = False
    for child in block.children:
        if get_title(child) == 'Video Library':
            tasks_attached = True
    if tasks_attached:
        print('\t', "Attached video, so skipping")
        return
    print('\t', "Attached video not found, so adding...")
    collection = client.get_collection(original_collection_view.collection.id)
    cvb = block.children.add_new(CollectionViewBlock, collection=collection)
    view = cvb.views.add_new(view_type="list")
    view.set('query2', get_filter(block, VIDEO_PROPERTY))

def get_title(child):
    return child.title if child and getattr(child, 'collection', None) else None

def get_filter(block, property):
    return {
            'filter': {
                'filters': [
                    {
                        'filter': {
                            'value': {
                                'type': 'exact',
                                'value': block.id
                            },
                            'operator': 'relation_contains'
                        },
                        'property': property
                    }
                ],
                'operator': 'and'
            },
            'group_by': ':tjE',
            'aggregations': [
                {
                    'aggregator': 'count'
                }
            ]
        }
FORMAT = {
            'list_properties': [
                {
                    'visible': False,
                    'property': 'j)H^'
                },
                {
                    'visible': False,
                    'property': '9iqC'
                }, {
                    'visible': True, 'property': 'h,N?'
                },
            ]
        }

if __name__ == '__main__':
    update_goals()