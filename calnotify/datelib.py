"""
datelib is a date parsing and math helper for calnotify.

Global config such as the local timezone are kept here to avoid polluting
the global namespace.
"""
from datetime import datetime, timedelta
from pytz import utc, timezone
import dateutil.parser

# global timezone used by this module
# update it with set_tz
tz = utc

# global date format use by this module
date_fmt = "%m/%d/%Y at %I:%M:%S %p"

# set to now as of the time this module is first imported
_now = datetime.utcnow()

# proxy isoparse into this module to keep date utils in one place and
# to avoid having to import dateutil.parser into both this module and
# the main app
isoparse = dateutil.parser.isoparse


def set_tz(tz_str: str):
    """
    Set the timezone globally within the datelib module
    :param tz_str: a timezone string (such as "US/Central")
    :return: None
    """
    global tz
    tz = timezone(tz_str)


def is_days_away(dt: datetime, days: int) -> bool:
    """
    Test to see if a datetime is more than days away, but less than days-1 from now.
    This function compares only the date components, not the time.
    :rtype: bool
    :param dt: datetime object to compare
    :param days: the number of days away the time must be
    :return: True if *dt* is *days* days away, else False
    """
    global _now
    day = timedelta(days=1)
    return _now.astimezone(tz).date()+(days*day) == dt.astimezone(tz).date()


def format_date(dt: datetime) -> str:
    """
    format a datetime according to the tz and date_fmt globally defined in datelib
    :rtype: str
    :param dt: datetime
    :return: a formatted string
    """
    return dt.astimezone(tz).strftime(date_fmt)
