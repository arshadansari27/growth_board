from dataclasses import dataclass
from typing import List

from jira import JIRA
from pymongo import MongoClient

from growth.config import CONFIG, JIRA_STOCKY_URL, JIRA_STOCKY_USER, JIRA_STOCKY_KEY, JIRA_PERSONAL_URL, \
    JIRA_PERSONAL_USER, JIRA_PERSONAL_KEY, DATABASE_URL, DATABASE_NAME
from growth.integration import OFFICE, PERSONAL
from growth.integration.notion_api import NotionDBv2


def import_jira_tasks():
    jira_mgr = JiraMgr()
    cards = list(jira_mgr.tasks.values())
    print("Starting jira update.....")
    for card in cards:
        print("[*] Card = ", card.key)
        Card.update_by_key(card)


class Repo:
    def __init__(self):
        self._collection = 'importer.jira'
        self.client = MongoClient(CONFIG[DATABASE_URL])
        self.database = getattr(self.client, CONFIG[DATABASE_NAME])

    @property
    def collection(self):
        return getattr(self.database, self._collection)

    def update_by_key(self, card: "Card"):
        self.collection.update({'_id': card.key}, {'$set': card.to_dict()}, upsert=True)

    def get_by_key(self, key: str):
        doc = self.collection.find_one({'_id': key})
        if not doc:
            return None
        return Card.from_dict(doc)

    def get_all(self):
        docs = self.collection.find_all()
        return [Card.from_dict(d) for d in docs]


repository = Repo()


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

    @classmethod
    def get_by_key(cls, key):
        return repository.get_by_key(key)

    @classmethod
    def update_by_key(cls, card: "Card"):
        repository.update_by_key(card)

    @classmethod
    def get_all(cls):
        return repository.get_all()

    @classmethod
    def from_dict(cls, dict_object):
        return Card(
            context=dict_object['context'],
            key=dict_object['key'],
            name=dict_object['name'],
            description=dict_object['description'],
            type=dict_object['type'],
            project_name=dict_object['project_name'],
            sub_task=dict_object['sub_task'],
            status=dict_object['status'],
            done=dict_object['done'],
            init=dict_object['init'],
            link=dict_object['link'],
            scheduled = dict_object['scheduled'],
            parent = dict_object['parent'],
            components = dict_object['components'],
            epic = dict_object['epic'],
            priority = dict_object['priority'],
            priority_name = dict_object['priority_name'],
        )

    def to_dict(self):
        return {
            'context': self.context,
            'key': self.key,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'project_name': self.project_name,
            'sub_task': self.sub_task,
            'status': self.status,
            'done': self.done,
            'init': self.init,
            'link': self.link,
            'scheduled': self.scheduled,
            'parent': self.parent,
            'components': self.components,
            'epic': self.epic,
            'priority': self.priority,
            'priority_name': self.priority_name,
        }


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
        elif context == PERSONAL:
            url = CONFIG[JIRA_PERSONAL_URL]
            user = CONFIG[JIRA_PERSONAL_USER]
            key = CONFIG[JIRA_PERSONAL_KEY]
            query = 'assignee in (557058:1184cd39-650a-4c1e-bd35-3a54abc2c637)'
        else:
            raise NotImplementedError
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


if __name__ == '__main__':
    import_jira_tasks()
