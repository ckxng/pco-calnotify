import datetime
import unittest

import datelib


class TestDatelib(unittest.TestCase):
    def test_set_tz(self):
        datelib.set_tz("US/Central")
        self.assertEqual(datelib.tz.zone, "US/Central")

    def test_is_days_away(self):
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow() + datetime.timedelta(days=1), 1), True)
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow() + datetime.timedelta(days=1), 2), False)
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow(), 0), True)
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow() - datetime.timedelta(days=1), -1), True)

    def test_format_date(self):
        self.assertEqual(datelib.format_date(datetime.datetime(2021, 8, 22, 22, 0, 18, 282081)),
                         '08/23/2021 at 03:00:18 AM')


if __name__ == '__main__':
    unittest.main()
