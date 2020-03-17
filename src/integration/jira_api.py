from dateutil import parser
from jira import JIRA

from config import CONFIG
from integration.notion_api import update_jira


def get_type(issue):
    return {'type': issue['issuetype']['name'], 'subtask': issue['issuetype']['subtask']}

def get_parent(issue):
    return {'parent': issue.get('parent', {}).get('key')}

def get_project(issue):
    return {'project': issue['project']['name'], 'project_key': issue['project']['key']}

def get_create_update_dates(issue):
    return {'created': parser.parse(issue['created']), 'updated': parser.parse(issue['updated'])}

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


def convert_issue(issue):
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

def get_stocky_jira():
    options = {'server': CONFIG['JIRA_STOCKY_URL']}
    jira = JIRA(
        options=options,
        basic_auth=(CONFIG['JIRA_STOCKY_USER'], CONFIG['JIRA_STOCKY_KEY']))
    return jira, 'assignee in (arshad)'

def get_personal_jira():
    options = {'server': CONFIG['JIRA_PERSONAL_URL']}
    jira = JIRA(
            options=options,
            basic_auth=(CONFIG['JIRA_PERSONAL_USER'], CONFIG[
                'JIRA_PERSONAL_KEY']))
    return jira, 'assignee in (557058:1184cd39-650a-4c1e-bd35-3a54abc2c637)'

if __name__ == '__main__':
    URL = CONFIG['NOTION_JIRA_URL']
    jira, search = get_personal_jira()
    issues = [convert_issue(i) for i in jira.search_issues(search)]
    update_jira(issues, 'Personal', URL)