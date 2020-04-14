import json

import requests
from dateutil.parser import parse
from notion.block import SubsubheaderBlock, TextBlock, CalloutBlock
from notion.collection import NotionDate
from requests.auth import HTTPBasicAuth

from growth.config import CONFIG, JIRA_STOCKY_URL, JIRA_STOCKY_USER, JIRA_STOCKY_KEY, NOTION_CONFLUENCE_DB
from growth.integration.notion_api import NotionDB
from growth.integration.scratch.html_to_markdown import read_body

URL = CONFIG[JIRA_STOCKY_URL]
USER = CONFIG[JIRA_STOCKY_USER]
KEY = CONFIG[JIRA_STOCKY_KEY]
CONFLUENCE_DB = CONFIG[NOTION_CONFLUENCE_DB]
auth = HTTPBasicAuth(USER, KEY)
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def get_author_info(data):
    created_by_id = data['history']['createdBy']['accountId']
    created_by_name = data['history']['createdBy']['publicName']
    created_date = data['history']['createdDate']
    return created_by_id, created_by_name, created_date

def get_children(data):
    ancestors = data.get('ancestors')
    children = data.get('children')
    descendants = data.get('descendants')
    return ancestors, children, descendants


def get_body(data):
    print(data['body'])
    body = data['body'].get('storage', {}).get('value', '')
    if not body:
        return []
    return read_body(body)


def get_page(page_id, tabs=''):
    expansion = ','.join([
        'childTypes.all', 'ancestors', 'body.export_view', 'body.storage', 'descendants', 'history', 'children.comment'])

    url = f'{URL}/wiki/rest/api/content/{page_id}?expand={expansion}'
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code == 404:
        print(f'--> Found nothing on {url}')
        return
    data = response.json()
    title = data['title']
    creator_id, creator_name, created_date = get_author_info(data)
    body = get_body(data)
    ancestors, children, descendants = get_children(data)
    ancestor_ids = [u['id'] for u in ancestors] if isinstance(ancestors, list) else []
    comment_ids = [u['id'] for u in children.get('comment', {}).get('results', [])]
    comments = []
    if comment_ids:
        url = f'{URL}/wiki/rest/api/content/{page_id}/child/comment?expand={expansion}'
        comment_response = requests.get(url, auth=auth, headers=headers)
        if comment_response.status_code >= 300:
            raise Exception("Comment ids exists but the code does not")
        for comment_data in comment_response.json()['results']:
            comment_id = comment_data['id']
            comment_title = comment_data['title']
            comment_creator_id, comment_creator_name, comment_created_date = get_author_info(comment_data)
            comment_body = get_body(comment_data)
            comment_details = {
                'id': comment_id,
                'title': comment_title,
                'creator_id': comment_creator_id,
                'creator_name': comment_creator_name,
                'created_date': comment_created_date,
                'body': comment_body,
            }
            comments.append(comment_details)
    child_ids = [u['id'] for u in children] if isinstance(children, list) else []
    descendant_ids = [u['id'] for u in descendants] if isinstance(descendants, list) else []
    page_details = {
        'title': title,
        'creator_id': creator_id,
        'creator_name': creator_name,
        'created_date': created_date,
        'ancestors': ancestor_ids,
        'descendants': descendant_ids,
        'children': child_ids,
        'comments': comments,
        'body': body
    }
    return page_details


def get_spaces():
    url = f'{URL}/wiki/rest/api/space'
    print('*', url)
    response = requests.get(url, auth=auth, headers=headers)
    print('*', response.text)
    spaces = {}
    response = response.json()
    for space in response['results']:
        spaces[space['id']] = {
            'name': space['name'],
            'key': space['key'],
            'type': space['type'],
            'status': space['status'],
            'pages': {}
        }
        if space['type'] == 'personal':
            continue
        key = space['key']
        if key != 'EN':
            print("[*] Skipping", key)
            continue
        start = 0
        limit = 25
        while True:
            page_url = f'{URL}/wiki/rest/api/content?spaceKey={key}&start={start}&limit={limit}'
            print(page_url)
            _response = requests.get(page_url, auth=auth, headers=headers)
            counter = 0
            for detail in _response.json()['results']:
                counter +=1
                if detail['type'] == 'personal':
                    continue
                page_details = get_page(detail['id'])
                spaces[space['id']]['pages'][detail['id']] = page_details
            start += limit
            if counter < limit:
                break
        print('[->] ', len(spaces[space['id']]['pages']))
    return spaces

def send_to_notion(data):
    # URL of the confluence collection
    db = NotionDB(CONFLUENCE_DB)
    page_dict = {}
    page_parent_dict = {}
    for space_id, space_details in data.items():
        space_name = space_details['name']
        space_key = space_details['key']
        space_type = space_details['type']
        space_status = space_details['status']
        pages = space_details['pages']
        for page_id, page_detail in pages.items():
            page_detail['space_name'] = space_name
            page_detail['space_id'] = space_id
            page_detail['space_key'] = space_key
            page_detail['space_status'] = space_status
            page_detail['space_type'] = space_type
            page_dict[page_id]  = page_detail
            if page_detail['ancestors']:
                page_parent_dict[page_id] = sorted(page_detail['ancestors'], key=lambda u: int(u))[-1]
    done_pages = set()
    stop = False
    page_dict_copy = {u:v for u,v in page_dict.items()}  # Copy to track ancestor look up
    while page_dict and not stop:
        print('Pass', len(page_dict.keys()),)
        page_ids_to_prune = []
        count = 0
        for page_id in page_dict:
            if page_id not in page_parent_dict or page_parent_dict[page_id] in done_pages:
                count += 1
                _send(db, page_id, page_dict[page_id], page_dict_copy)
                page_ids_to_prune.append(page_id)
                done_pages.add(page_id)
        for page_id in page_ids_to_prune:
            page_dict.pop(page_id)
        print('\tDone', len(done_pages))


def _send(db, _page_id, _page_detail, page_dict):
    page = db.get_or_create(f"{_page_detail['title']} ({_page_id})")
    print(page.title)
    if getattr(page, 'Imported', False) is True:
        print("\tSkip already done...")
        return
    existing_page_id = getattr(page, 'Page Id')
    assert not existing_page_id or _page_id.strip() == existing_page_id.strip()
    print('\tSetting Attribs')
    if getattr(page, 'Page Id', None) != _page_id:
        setattr(page, 'Page Id', _page_id)
    if getattr(page, 'Space', None) != _page_detail['space_name']:
        setattr(page, 'Space', _page_detail['space_name'])
    if getattr(page, 'Space Id', None) != _page_detail['space_id']:
        setattr(page, 'Space Id', _page_detail['space_id'])
    if getattr(page, 'Space Key', None) != _page_detail['space_key']:
        setattr(page, 'Space Key', _page_detail['space_key'])
    created_at = NotionDate(parse(_page_detail['created_date']))
    if getattr(page, 'Created At', None) != created_at:
        setattr(page, 'Created At', created_at)
    if getattr(page, 'Author', None) != _page_detail['creator_name']:
        setattr(page, 'Author', _page_detail['creator_name'])
    if getattr(page, 'Author Id', None) != _page_detail['creator_id']:
        setattr(page, 'Author Id', _page_detail['creator_id'])
    if getattr(page, 'Ancestors', None) != ','.join(_page_detail['ancestors']):
        setattr(page, 'Ancestors', ','.join(_page_detail['ancestors']))

    ancestor = sorted(_page_detail['ancestors'], key=lambda u: int(u))[-1] if _page_detail['ancestors'] else None
    if ancestor:
        parent = db.get_or_create(f"{page_dict[ancestor]['title']} ({ancestor})")
        if parent:
            if getattr(page, 'Ancestor', None) != parent.id:
                setattr(page, 'Ancestor', parent.id)
        else:
            print("This is bad, how can there not be an ancestor", page.title, ancestor, parent)
    page_block = db.client.get_block(page.id, force_refresh=True)
    print('\tCleaning Up Content')
    for child in page_block.children:
        child.remove()
    print('\tSetting Content')
    page_block.children.add_new(SubsubheaderBlock, title='Details')
    for line in _page_detail['body']:
        if not line.strip():
            continue
        page_block.children.add_new(TextBlock, title=line)
    page_block.children.add_new(SubsubheaderBlock, title='Comments')
    comments = sorted(_page_detail['comments'], key=lambda u: parse(u['created_date']), reverse=True)
    for comment in comments:
        comment_title = comment['title']
        comment_created_at = comment['created_date']
        comment_creator = comment['creator_name']
        comment_body = comment['body']
        comment_text = f"[{comment_created_at}] {comment_creator} says: {comment_title}\n\n{comment_body}"
        page_block.children.add_new(CalloutBlock, title=comment_text)
    if not getattr(page, 'Has Comments', False) and comments:
        setattr(page, 'Has Comments', True)
    setattr(page, 'Imported', True)


if __name__ == '__main__':
    with open('space_data.json', 'w') as outfile:
        outfile.write(json.dumps(get_spaces(), indent=4))
    with open('space_data.json') as infile:
        send_to_notion(json.loads(infile.read()))
    #get_page('70226759')




