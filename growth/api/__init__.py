from flask import Flask
from growth.config import CONFIG, AUTH_USER, AUTH_PASSWORD
from .authentication import requires_auth


app = Flask(__name__)


@app.route('/calendar/task', methods=['GET'])
def task_calendar():
    return ''


@app.route('/update/tasks', methods=['POST'])
@requires_auth
def update_tasks():
    from growth.integration.notion_api import update_tasks as task_updater
    task_updater()
    return ''


@app.route('/update/hiring', methods=['POST'])
@requires_auth
def update_hiring():
    from growth.integration.notion_api import update_from_hiring_board
    update_from_hiring_board()
    return ''


@app.route('/update/tracker', methods=['POST'])
@requires_auth
def update_tracker():
    from growth.integration.notion_api import update_tracker as tracker_updater
    tracker_updater()
    return ''


@app.route('/update/calendar', methods=['POST'])
@requires_auth
def update_calendar():
    from growth.integration.notion_api import update_calendar_times
    update_calendar_times()
    return ''


@app.route('/update/calendar-primary', methods=['POST'])
@requires_auth
def update_calendar_primary():
    from growth.integration.notion_api import update_all_events_from_primary
    update_all_events_from_primary()
    return ''


# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

