import pickle
import os.path
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_creds(token_path: str) -> Optional[Credentials]:
    """
    Validate if the token.pickle exists. If the credentials do not exist or are
    not valid we initiate the authentication with Google.
    """
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # If the credentials have expired we refresh them.
            creds.refresh(Request())
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            return creds

    return creds


def login(token_path: str) -> Optional[Credentials]:
    """
    Trigger the authentication so that we can store a new token.pickle.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
        'gcal/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)

    return creds
