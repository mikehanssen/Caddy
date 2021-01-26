# -*- coding: utf-8 -*-
import os
import sys
import json
import datetime
import webbrowser
from time import sleep
from threading import Thread
from os.path import expanduser
from typing import Optional, List, Any, Dict

import rumps
from rumps import MenuItem, quit_application
from dateutil.parser import parse
from google.oauth2.credentials import Credentials

from gcal import auth
from gcal import calendar

HOME_PATH = expanduser('~')
BASE_PATH = os.path.join(HOME_PATH, 'Library/Caddy')
rumps.debug_mode(True)


@rumps.notifications
def notifications(notification: Dict[str, Any]) -> None:
    """
    Receives the data that was passed to a notification once it's clicked.
    """
    # TODO: Implement more handlers than just Google Meet link opening.
    webbrowser.open(notification['hangoutLink'])


def _create_app_dir():
    """
    Create a directory in the Library to store configuration files.
    """
    os.makedirs(BASE_PATH, exist_ok=True)


def _token_path() -> str:
    """
    Return the Google pickle file path.
    """
    return os.path.join(BASE_PATH, 'token.pickle')


class Notification:
    @classmethod
    def run(cls, countdown: int, title: str, subtitle: str, message: str,
            action_button: Optional[str] = None,
            data: Optional[Dict[str, any]] = None):
        """
        Trigger an timer that will countdown until the meeting almost starts and
        will than notify you with a simple Google Meet join link.
        """

        def timer():
            for i in range(countdown):
                sleep(1)
            rumps.notification(
                title=title, subtitle=subtitle, message=message, data=data,
                action_button=action_button, icon='static/icon.png')
            sys.exit()

        t1 = Thread(target=timer)
        t1.start()


class Caddy(rumps.App):
    _authenticated = False  # type: bool
    _credentials = None  # type: Credentials
    _events = None  # type: Optional[List[Dict[Any, Any]]]

    serializer = json

    CALENDAR_URL = 'https://calendar.google.com/calendar/u/0/r/week'

    def __init__(self, *args, **kwargs) -> None:
        """
        Overwrite the init because we want to create dynamic menu items.
        """
        super().__init__(
            *args,
            **kwargs,
            quit_button=None)
        self.icon = 'static/icon.png'

        _create_app_dir()
        self._refresh()

    def _refresh(self):
        """
        First we refresh the menu and title. Afterwards we oad the credentials
        and refresh all menu items.
        """
        self.menu.clear()
        self._events = []
        self.title = None

        self.credentials = auth.get_creds(_token_path())
        self._authenticated = self.credentials is not None

        if self._authenticated:
            self.load_events()

        self._refresh_menu()
        self._refresh_title()

    def _refresh_title(self):
        """
        If we have events we modify the title of the menu item to display the
        title and start time of the next calendar item. We set the timer by
        calculating the amount of seconds between now and the meeting.

        We give the notification 120 seconds before the start of the meeting.
        """
        if self._events is not None and len(self._events) > 0:
            start = parse(self._events[0]['start']['dateTime'])
            now = datetime.datetime.now().astimezone()
            self.title = \
                f'{start.strftime("%a %H:%M")} - {self._events[0]["summary"]}'
            Notification.run(
                countdown=(start - now).seconds - 120,
                title='Meeting starting soon',
                data=self._events[0],
                subtitle=self._events[0]['summary'],
                message='Click here to join',
                action_button='Join Meet')

    def _refresh_menu(self):
        """
        Load the menu items, if the user is not authenticated we display the
        configure menu with the supported platforms.
        """
        if not self._authenticated:
            self.menu = [
                [MenuItem('Configure'), [
                    MenuItem('Google Calendar', callback=self.configure_google)
                ]],
                None,
                MenuItem('Quit', key='q', callback=quit_application)
            ]
        else:
            self.menu = [
                MenuItem(
                    'Open Calendar',
                    callback=lambda _: webbrowser.open(self.CALENDAR_URL)),
                [MenuItem('Upcoming Items'), self._create_event_items()],
                None,
                MenuItem('Logout', callback=self.logout),
                None,
                MenuItem('Quit', key='q', callback=quit_application)
            ]

    def _event_menu_item(self, event) -> MenuItem:
        """
        Generate a menu item for an event. The callback will navigate the user
        to the agenda item in the browser.
        """
        start = parse(event['start']['dateTime'])
        return MenuItem(
            f'{start.strftime("%m-%d %H:%M")} - {event["summary"]}',
            callback=lambda _: webbrowser.open(event['htmlLink']))

    def _create_event_items(self):
        """
        Generate menu items for the first 10 upcoming event items. We generate
        a menu item with the title and the date and summary. If you click on it
        you will be navigated to the browser item of the event. 
        """
        return [self._event_menu_item(event) for event in self._events]

    def load_events(self):
        """
        Load the upcoming events.
        """
        self._events = calendar.upcoming_events(self.credentials)

    def logout(self, _) -> None:
        """
        Remove the stored config file.
        """
        os.remove(_token_path())
        self._refresh()

    def configure_google(self, _) -> None:
        """
        We trigger a login with the Google Services.
        """
        auth.login(_token_path())
        self._refresh()


if __name__ == '__main__':
    Caddy('📅').run()
