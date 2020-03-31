from dataclasses import dataclass
from typing import List

from jira import JIRA
from notion.block import CalloutBlock

from config import CONFIG, JIRA_STOCKY_URL, JIRA_STOCKY_USER, JIRA_STOCKY_KEY, \
    NOTION_TASKS_URL, NOTION_PROJECT_URL
from notion_api import NotionDB

PERSONAL = 'Personal'
OFFICE = 'Office'


@dataclass
class Card:
    context: str
    key: str
    name: str
    description: str
    type: str
    project_name: str
    sub_task: bool
    status: str
    done: bool
    init: bool
    link: str
    scheduled: str = None
    parent: str = None
    components: List[str] = None
    epic: str = None
    priority: int = None
    priority_name: str = None

    def __repr__(self):
        return f"[{self.type}]: {self.name} ({self.status})"


class JiraContextMgr:
    def __init__(self, context, config):
        self.context = context
        url, user, key, query = config
        options = {'server': url}
        self.jira = JIRA(
                options=options,
                basic_auth=(user, key))
        self.query = query

    def get_cards(self) -> List[Card]:
        cards = [convert_issue(self.context, i) for i in
                 self.jira.search_issues(self.query)]
        return cards

    @classmethod
    def get_jira(cls, context):

        if context == OFFICE:
            url = CONFIG[JIRA_STOCKY_URL]
            user = CONFIG[JIRA_STOCKY_USER]
            key = CONFIG[JIRA_STOCKY_KEY]
            query = 'assignee in (arshad)'

        else:
            raise NotImplementedError
        '''
        if context == PERSONAL:
            url = CONFIG[JIRA_PERSONAL_URL]
            user = CONFIG[JIRA_PERSONAL_USER]
            key= CONFIG[JIRA_PERSONAL_KEY]
            query = 'assignee in (557058:1184cd39-650a-4c1e-bd35-3a54abc2c637)'
        '''
        return JiraContextMgr(context, (url, user, key, query))


def convert_issue(context, issue) -> Card:
    key = issue.key.strip()
    link = issue.permalink()
    issue = issue.raw['fields']
    status =  issue['status']['name']
    type =  issue['issuetype']['name']
    minor =  issue['issuetype']['subtask']
    parent =  issue.get('parent', {}).get('key')
    priority = int(issue['priority']['id'])
    priority_name = issue['priority']['name']
    project_name = issue['project']['name']
    components = [u['name'] for u in issue['components']] if \
        issue.get('components') else []
    description = issue['description']
    summary = issue['summary'].strip()
    card = Card(
        context,
        key,
        summary,
        description,
        type,
        project_name,
        minor,
        status,
        bool(status in {'Done', 'No Action', 'Published'}),
        bool(status in {'Backlog', 'To Do'}),
        link,
        '',
        parent,
        components=components,
        epic=None,
        priority=priority,
        priority_name=priority_name
    )
    return card


class JiraMgr:
    def __init__(self):
        cards = {}
        office = JiraContextMgr.get_jira(OFFICE)
        for card in office.get_cards():
            cards[card.key] = card
        self.tasks = cards


task_field_mapping = {
        'context': 'context',
        'summary': 'name',
        'type': 'type',
        'minor': 'sub_task',
        'status': 'status',
        'done': 'done',
        'init': 'init',
        'link': 'link',
        'parent_name': 'parent',
        'epic': 'epic',
        'priority': 'priority',
        'priority_name': 'priority_name'
    }


def update_notion_jira_tasks(task_db, project_db):
    jira_mgr = JiraMgr()
    cards = list(jira_mgr.tasks.values())
    print("Starting jira update.....")
    for card in cards:
        print("[*] Card = ", card.key)
        project = project_db.get_or_create(card.project_name)
        print("\t", project)
        task = task_db.get_or_create(card.key)
        print("\t", task)
        if task.project != project.id:
            task.project = project.id
        for k, v in task_field_mapping.items():
            u = getattr(task, k, None)
            w = getattr(card, v, None)
            if u != w and w is not None:
                print('\t\t', task.title, k, u, v, w)
                setattr(task, k, w)
        if card.components and sorted(card.components) != sorted(
                task.components):
            task.components = card.components
        if card.description:
            clean_and_update_page_area_of_row(card.description, task,
                                              task_db.client)


def clean_and_update_page_area_of_row(description, task, client):
        block = client.get_block(task.id)
        title = f'Description\n\n{description}'
        found = False
        for child in block.children:
            if child.title == title:
                found = True
                break
        if not found:
            block.children.add_new(
                CalloutBlock, title=title)


if __name__ == '__main__':
    update_notion_jira_tasks()

