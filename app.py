import json
import os

import requests
import yaml
from dotenv import load_dotenv

from calnotify.datelib import is_days_away, set_tz, format_date, isoparse
from calnotify.sendlib import sendsms, sendmail

# vars used during development in this app module, as well as calnotify.sendlib
load_dotenv()


def build_notify_list() -> dict:
    """
    open contacts.yaml and build the notification list indexed by the number of days out for notifications.
    The file should contain contents such as:

        ---
        groups:
          - name: "Next Day"
            days: 1
            contacts:
              - type: "email"
                to: "address@example.com"
              - type: "sms"
                to: "+15551234567"

          - name: "Day After Tomorrow"
            days: 2
            contacts:
              - type: "email"
                to: "address@example.com"
              - type: "sms"
                to: "+15551234567"

          - name: "In One Week"
            days: 7
            contacts:
              - type: "email"
                to: "address@example.com"
              - type: "sms"
                to: "+15551234567"

    :rtype dict
    :return: notify list
    """
    notify_list = {}
    with open('contacts.yaml', 'r') as file:
        for group in yaml.safe_load(file)['groups']:
            notify_list[group['days']] = group['contacts']
    return notify_list


def get_pco_calendar() -> dict:
    """
    Connects to the Planning Center Calendar API (v2) to retrieve future calendar
    events matching a particular tag as configured in the following environment
    variables:

        PCOTAGID - tag id to filter by
        PCOPERPAGE - number of responses
        PCOAPPID - Application ID for API access
        PCOSECRET - Secret for API access

    :rtype dict
    :return: parsed JSON response from Planning Center Calendar API
    """
    return json.loads(requests.get(
        'https://api.planningcenteronline.com' +
        '/resources/v2/event_instances' +
        '?filter=future&order=starts_at&include=event_times,event' +
        '&where[tag_ids]=' + os.environ['PCOTAGID'] +
        '&per_page=' + os.environ['PCOPERPAGE'],
        auth=(os.environ['PCOAPPID'], os.environ['PCOSECRET'])).text)


def build_events(data) -> (dict, dict):
    """
    Builds two dicts based on the JSON object data returned by get_pco_calendar()
    - events: a list containing event data
    - event_times: a dict mapping event_time IDs to event_time data

    :rtype (dict, dict)
    :param data:
    :return: tuple containing (events, event_times)
    """
    events = {}
    event_times = {}
    for included in data['included']:
        if included['type'] == 'Event':
            events[included['id']] = included['attributes']
        elif included['type'] == 'EventTime':
            event_times[included['id']] = included['attributes']
    return events, event_times


def notify_contact(contact, ev, days_away, et_start_str, et_end_str, instance) -> None:
    """
    notify a contact by email and/or sms depending on contact type
    :rtype None
    :param contact: individual contact from the notify_list
    :param ev: general event definition object
    :param days_away: how many days away this notification is
    :param et_start_str: event time start string
    :param et_end_str: event time end string
    :param instance: event instance object
    :return: None
    """
    if contact['type'] == 'email':
        print('email:', contact['to'])
        sendmail(contact['to'], os.environ['PREFIX'] + ev['name'] + ' at ' + et_start_str, """
Don't forget!  There is an event coming up in %s days!

Event: %s
Time: from %s to %s
Location: %s
""" % (days_away, ev['name'], et_start_str, et_end_str, instance['attributes']['location']))

    elif contact['type'] == 'sms':
        print('sms:', contact['to'])
        sendsms(contact['to'], os.environ['PREFIX'] + ev['name'] + ' at ' + et_start_str)


def identify_applicable_event_times(events, instance, event_times, notify_list, days_away) -> None:
    """
    Identity applicable times (where 'visible_on_widget_and_ical is True) and send notifications
    to all contacts in that group.

    :rtype None
    :param events: a list containing event data
    :param instance: event instance object
    :param event_times: a dict mapping event_time IDs to event_time data
    :param notify_list: the notification list dict
    :param days_away: how many days away this notification is
    :return: None
    """
    ev = events[instance['relationships']['event']['data']['id']]

    # look inside the event for specific times
    # only notify about published times (not things like "setup" or "teardown")
    times = instance['relationships']['event_times']['data']
    for time in times:
        if event_times[time['id']]['visible_on_widget_and_ical']:
            et_start_str = format_date(isoparse(event_times[time['id']]['starts_at']))
            et_end_str = format_date(isoparse(event_times[time['id']]['ends_at']))

            # notify all contacts in the notify list
            for contact in notify_list[days_away]:
                notify_contact(contact, ev, days_away, et_start_str, et_end_str, instance)


def evaluate_instance(notify_list, start_dt, events, instance, event_times) -> None:
    """
    Evaluate whether or not an event instance is the correct number of days away.
    If it is, notify the applicable group.

    :rtype None
    :param notify_list: the notification list dict
    :param start_dt: the datetime object representing the event start date
    :param events: a list containing event data
    :param instance: event instance object
    :param event_times: a dict mapping event_time IDs to event_time data
    :return: None
    """
    # for each group in the notify list, is this event in the specified range?
    for days_away in notify_list.keys():
        if is_days_away(start_dt, days_away):
            identify_applicable_event_times(events, instance, event_times, notify_list, days_away)


def main():
    set_tz(os.environ['TZ'])

    notify_list = build_notify_list()
    data = get_pco_calendar()
    (events, event_times) = build_events(data)

    # read all instances from the response data
    for instance in data['data']:
        # look up when this event starts
        start_dt = isoparse(instance['attributes']['starts_at'])

        evaluate_instance(notify_list, start_dt, events, instance, event_times)


if __name__ == '__main__':
    main()
