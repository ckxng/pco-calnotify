from dotenv import load_dotenv
import requests
import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from calnotify.datelib import is_days_away, set_tz, format_date, parse_and_format_date, isoparse

load_dotenv()
set_tz(os.environ['TZ'])


def sendmail(to, subject, text):
    """
    Send a plain text email
    :param to: the email address to send to
    :param subject: the email subject
    :param text: the plain text message to send
    """
    message = Mail(
        from_email=os.environ['MAILFROM'],
        to_emails=to,
        subject=subject,
        plain_text_content=text)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRIDAPIKEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def sendsms(to, text):
    """
    Sends a SMS
    :param to: phone number in string format matching +15551234567
    :param text: the plain text message to send
    """
    client = Client(os.environ.get('TWILIOSID'), os.environ.get('TWILIOTOKEN'))

    message = client.messages.create(
        messaging_service_sid=os.environ.get('TWILIOSERVICESID'),
        body=text,
        to=to
    )

    print(message.sid)


data = json.loads(requests.get(
    'https://api.planningcenteronline.com' +
    '/resources/v2/event_instances' +
    '?filter=future&order=starts_at&include=event' +
    '&where[tag_ids]=' + os.environ['PCOTAGID'] +
    '&per_page=' + os.environ['PCOPERPAGE'],
    auth=(os.environ['PCOAPPID'], os.environ['PCOSECRET'])).text)

# read events from response data and reindex it in a hash by (str)id
events = {}
for event in data['included']:
    if event['type'] != 'Event':
        continue
    events[event['id']] = event['attributes']

# read all instances from the response data
for instance in data['data']:
    days_away = 1
    start_dt = isoparse(instance['attributes']['starts_at'])
    if is_days_away(start_dt, days_away):
        ev = events[instance['relationships']['event']['data']['id']]
        print('email:')
        sendmail(os.environ['TESTMAILTO'],
                 os.environ['PREFIX'] + ev['name'] + ' at ' + format_date(start_dt),
                 """
Don't forget!  There is an event coming up in %s days!

Event: %s
Time: from %s to %s
Location: %s
""" % (days_away, ev['name'], format_date(start_dt),
       parse_and_format_date(instance['attributes']['ends_at']),
       instance['attributes']['location']))

        sendsms(os.environ['TESTSMSTO'],
                os.environ['PREFIX'] + ev['name'] + ' at ' + format_date(start_dt))
