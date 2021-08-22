"""
an email and SMS sending library for the pco-calnotify app
"""
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client


def sendmail(to, subject, text, sendgridapikey=None, mailfrom=None):
    """
    Send a plain text email
    If apikey is not provided, it will be fetched from os.environ['SENDGRIDAPIKEY']
    If mailfrom is not provided, it will be fetched from os.environ['MAILFROM']

    If os.environ['TESTMODE']=='1', this function will return without taking action
    :param to: the email address to send to
    :param subject: the email subject
    :param text: the plain text message to send
    :param sendgridapikey: SendGrid API Key
    :param mailfrom: email address to send from
    """
    # do not actually send messages in TESTMODE
    if os.environ.get('TESTMODE', None) == '1':
        return

    # raise exceptions when required params are missing
    if sendgridapikey is None:
        sendgridapikey = os.environ['SENDGRIDAPIKEY']
    if mailfrom is None:
        mailfrom = os.environ['MAILFROM']

    # send the message
    SendGridAPIClient(sendgridapikey).send(Mail(
        from_email=mailfrom,
        to_emails=to,
        subject=subject,
        plain_text_content=text))


def sendsms(to, text, twiliosid=None, twiliotoken=None, twilioservicesid=None):
    """
    Sends a SMS
    If twiliosid is not provided, it will be fetched from os.environ['TWILIOSID'].
    If twiliotoken is not provided, it will be fetched from os.environ['TWILIOTOKEN'].
    If twilioservicesid is not provided, it will be fetched from os.environ['TWILIOSERVICESID'].

    If os.environ['TESTMODE']=='1', this function will return without taking action
    :param to: phone number in string format matching +15551234567
    :param text: the plain text message to send
    :param twiliosid: the Twilio SID
    :param twiliotoken: the Twilio Token
    :param twilioservicesid: the Twilio Messaging Service SID
    """
    # do not actually send messages in TESTMODE
    if os.environ.get('TESTMODE', None) == '1':
        return

    # raise exceptions when required params are missing
    if twiliosid is None:
        twiliosid = os.environ['TWILIOSID']
    if twiliotoken is None:
        twiliotoken = os.environ['TWILIOTOKEN']
    if twilioservicesid is None:
        twilioservicesid = os.environ['SERVICESSID']

    # send the message
    Client(twiliosid, twiliotoken).messages.create(
        messaging_service_sid=twilioservicesid,
        body=text,
        to=to)
