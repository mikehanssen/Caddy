import datetime
from typing import List, Dict, Any

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def upcoming_events(credentials: Credentials) -> List[Dict[Any, Any]]:
    """
    Retrieve the first upcoming 10 calendar items.
    """
    service = build('calendar', 'v3', credentials=credentials)

    # Call the Calendar API
    now = datetime.datetime.now().astimezone().isoformat()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events
