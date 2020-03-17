from dataclasses import dataclass
from typing import List, Callable, Tuple, Any

from dateutil import parser
from jira import JIRA

from config import CONFIG
from integration.notion_api import update_project_info


@dataclass
class Card:
    type: str
    project: str
    on_going: List[str]
    up_next: List[str]
    done: int = 0
    total: int = 0
    sub_done: int = 0
    sub_total: int = 0


def convert_issue(issue):
    def get_type(issue):
        return {'type': issue['issuetype']['name'],
                'subtask': issue['issuetype']['subtask']}

    def get_parent(issue):
        return {'parent': issue.get('parent', {}).get('key')}

    def get_project(issue):
        return {'project': issue['project']['name'],
                'project_key': issue['project']['key']}

    def get_create_update_dates(issue):
        return {'created': parser.parse(issue['created']),
                'updated': parser.parse(issue['updated'])}

    def get_status(issue):
        return {'status': issue['status']['name']}

    def get_components(issue):
        return {'components': [u['name'] for u in issue['components']] if
        issue.get(
                'components') else []}

    def get_description(issue):
        return {'description': issue['description']}

    def get_title(issue):
        return {'title': issue['summary']}

    _issue = {'key': issue.key}
    _issue['link'] = issue.permalink()
    issue = issue.raw['fields']
    _issue.update(get_type(issue))
    _issue.update(get_parent(issue))
    _issue.update(get_project(issue))
    _issue.update(get_create_update_dates(issue))
    _issue.update(get_status(issue))
    _issue.update(get_components(issue))
    _issue.update(get_description(issue))
    _issue.update(get_title(issue))
    return _issue


def get_stocky_jira() -> Tuple[JIRA, str]:
    options = {'server': CONFIG['JIRA_STOCKY_URL']}
    jira = JIRA(
        options=options,
        basic_auth=(CONFIG['JIRA_STOCKY_USER'], CONFIG['JIRA_STOCKY_KEY']))
    return jira, 'assignee in (arshad)'


def get_personal_jira() -> Tuple[JIRA, str]:
    options = {'server': CONFIG['JIRA_PERSONAL_URL']}
    jira = JIRA(
            options=options,
            basic_auth=(CONFIG['JIRA_PERSONAL_USER'], CONFIG[
                'JIRA_PERSONAL_KEY']))
    return jira, 'assignee in (557058:1184cd39-650a-4c1e-bd35-3a54abc2c637)'


def create_cards(jira_factory: Callable[[], Tuple[JIRA, str]], context, cards):
    jira, search = jira_factory()
    print(context, "Getting issues")
    issues = [convert_issue(i) for i in jira.search_issues(search)]
    print(context, "Converting issues")
    for issue in issues:
        print(issue['key'])
        if issue['project'] not in cards:
            card = Card(context, issue['project'], [], [])
            cards[issue['project']] = card
        else:
            card = cards[issue['project']]
        if issue['subtask']:
            card.sub_total += 1
        card.total += 1
        key, summary, type, link = issue['key'], issue['title'], \
                                   issue['type'], issue['link']
        text = f"**{type}**: ***{key}*** - [{summary}]({link})"
        if issue['status'].lower() in {'published', 'done', 'no action'}:
            if issue['subtask']:
                card.sub_done += 1
            card.done += 1
        elif issue['status'].lower() in {'in progress', 'draft'}:

            card.on_going.append(text)
        elif issue['status'].lower() == 'selected for development':
            card.up_next.append(text)
    print(context, "Done creating cards...", len(cards))
    return cards


def update_notion_projects():
    cards = {}
    cards = create_cards(get_personal_jira, 'Personal', cards)
    cards = create_cards(get_stocky_jira, 'Office', cards)
    update_project_info(cards)

