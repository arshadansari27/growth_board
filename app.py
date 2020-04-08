from functools import wraps

from flask import Flask, request, Response

from config import CONFIG, AUTH_USER, AUTH_PASSWORD

app = Flask(__name__)


def check_auth(username, password):
    _username, _password = CONFIG[AUTH_USER], CONFIG[AUTH_PASSWORD]
    return username == _username and password == _password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        "Could not verify your access level for that URL.\n" "You have to login with proper credentials",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/calendar/task', methods=['GET'])
def task_calendar():
    return ''


@app.route('/update/tasks', methods=['POST'])
@requires_auth
def update_tasks():
    from notion_api.task_updater import update_tasks as task_updater
    task_updater()


@app.route('/update/hiring', methods=['POST'])
@requires_auth
def update_hiring():
    from notion_api.task_updater import update_from_hiring_board
    update_from_hiring_board()

    
@app.route('/update/jira', methods=['POST'])
@requires_auth
def update_jira():
    from notion_api.task_updater import update_notion_jira_tasks
    update_notion_jira_tasks()


@app.route('/update/tracker', methods=['POST'])
@requires_auth
def update_tracker():
    from notion_api.tracker_updater import update_tracker as tracker_updater
    tracker_updater()


@app.route('/update/calendar', methods=['POST'])
@requires_auth
def update_calendar():
    from notion_api.calendar_updater import update_calendar_times
    update_calendar_times()


# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"



if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    #app.run(threaded=True, port=5000)
    app.run(debug=True, port=5000)
