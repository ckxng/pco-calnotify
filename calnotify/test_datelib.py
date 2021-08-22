import unittest
import datelib
import datetime


class TestDatelib(unittest.TestCase):
    def test_set_tz(self):
        datelib.set_tz("US/Central")
        self.assertEqual(datelib.tz.zone, "US/Central")

    def test_is_days_away(self):
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow() + datetime.timedelta(days=1), 1), True)
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow() + datetime.timedelta(days=1), 2), False)
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow(), 0), True)
        self.assertEqual(datelib.is_days_away(datetime.datetime.utcnow() - datetime.timedelta(days=1), -1), True)


if __name__ == '__main__':
    unittest.main()
