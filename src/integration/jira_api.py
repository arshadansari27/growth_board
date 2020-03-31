from dataclasses import dataclass
from typing import List

from jira import JIRA
from notion.block import CalloutBlock

from config import CONFIG
from integration.notion_api import NotionDB

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
            url = CONFIG['JIRA_STOCKY_URL']
            user = CONFIG['JIRA_STOCKY_USER']
            key = CONFIG['JIRA_STOCKY_KEY']
            query = 'assignee in (arshad)'

        else:
            raise NotImplementedError
        '''
        if context == PERSONAL:
            url = CONFIG['JIRA_PERSONAL_URL']
            user = CONFIG['JIRA_PERSONAL_USER']
            key= CONFIG['JIRA_PERSONAL_KEY']
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


def update_notion_jira_tasks():
    jira_mgr = JiraMgr()
    task_db = NotionDB(CONFIG['NOTION_TASKS_URL'])
    goal_db = NotionDB(CONFIG['NOTION_GOALS_URL'])
    cards = list(jira_mgr.tasks.values())
    for card in cards:
        goal = goal_db.get_or_create(card.project_name)
        task = task_db.get_or_create(card.key)
        if task.goal != goal.id:
            task.goal = goal.id
        for k, v in task_field_mapping.items():
            if getattr(task, k, None) != getattr(card, v, False):
                setattr(task, k, getattr(card, v, None))
        if card.components and sorted(card.components) != sorted(
                task.components):
            task.components = card.components
        if card.description:
            clean_and_update_page_area_of_row(card.description, task,
                                              task_db.client)


def clean_and_update_page_area_of_row(description, task, client):
        block = client.get_block(task.id)
        for child in block.children:
            child.remove(permanently=True)
        block.children.add_new(
            CalloutBlock, title=f'Description\n\n{description}')


if __name__ == '__main__':
    update_notion_jira_tasks()

