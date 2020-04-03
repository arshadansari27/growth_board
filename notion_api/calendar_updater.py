from config import CONFIG, GOOGLE_CREDS_PERSONAL, GOOGLE_CREDS_OFFICE
from integration.calendar_google_api import GoogleCalendar

def calendar_events():
    p_calendar = GoogleCalendar('Personal', CONFIG[GOOGLE_CREDS_PERSONAL])
    o_calendar = GoogleCalendar('Office', CONFIG[GOOGLE_CREDS_OFFICE])
    print(list(p_calendar.get_events()))
    print(list(o_calendar.get_events()))

if __name__ == '__main__':
    calendar_events()
